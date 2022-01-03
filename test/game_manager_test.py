from __future__ import annotations
import unittest
from typing import List, Tuple, Dict, Callable, Type, Set
import os
import time
from datetime import datetime
import uuid
from src.austin_heller_repo.game_manager import GameManagerClientServerMessage, GameManagerStructureFactory, AuthenticateClientRequestGameManagerClientServerMessage, AuthenticateClientResponseGameManagerClientServerMessage, UrlNavigationNeededResponseGameManagerClientServerMessage, GameManagerClientServerMessageTypeEnum, ClientAlreadyAuthenticatedErrorGameManagerClientServerMessage
from austin_heller_repo.client_authentication_manager import ClientAuthenticationClientServerMessage
from austin_heller_repo.socket_queued_message_framework import ClientMessengerFactory, ServerMessengerFactory, ClientServerMessage
from austin_heller_repo.socket import ClientSocketFactory, ServerSocketFactory
from austin_heller_repo.common import HostPointer
from austin_heller_repo.threading import SingletonMemorySequentialQueueFactory, Semaphore, start_thread


def get_default_host_port() -> int:
	return 35125


def get_default_client_authentication_port() -> int:
	return 35124  # NOTE this is what the client_authentication_manager_service is listening on


def get_default_client_messenger_factory() -> ClientMessengerFactory:
	return ClientMessengerFactory(
		client_socket_factory=ClientSocketFactory(
			to_server_packet_bytes_length=4096
		),
		server_host_pointer=HostPointer(
			host_address="localhost",
			host_port=get_default_host_port()
		),
		client_server_message_class=GameManagerClientServerMessage,
		is_debug=True
	)


def get_default_server_messenger_factory() -> ServerMessengerFactory:
	return ServerMessengerFactory(
		server_socket_factory=ServerSocketFactory(
			to_client_packet_bytes_length=4096,
			listening_limit_total=10,
			accept_timeout_seconds=1.0
		),
		sequential_queue_factory=SingletonMemorySequentialQueueFactory(),
		local_host_pointer=HostPointer(
			host_address="localhost",
			host_port=get_default_host_port()
		),
		client_server_message_class=GameManagerClientServerMessage,
		structure_factory=GameManagerStructureFactory(
			client_authentication_client_messenger_factory=ClientMessengerFactory(
				client_socket_factory=ClientSocketFactory(
					to_server_packet_bytes_length=4096
				),
				server_host_pointer=HostPointer(
					host_address="localhost",
					host_port=get_default_client_authentication_port()
				),
				client_server_message_class=ClientAuthenticationClientServerMessage,
				is_debug=True
			),
			authentication_timeout_seconds=10
		),
		is_debug=True
	)


class GameManagerTest(unittest.TestCase):

	def test_initialize(self):

		client_messenger_factory = get_default_client_messenger_factory()

		self.assertIsNotNone(client_messenger_factory)

		server_messenger_factory = get_default_server_messenger_factory()

		self.assertIsNotNone(server_messenger_factory)

	def test_client_authentication_client_server_message(self):

		client_server_message_type_class = ClientAuthenticationClientServerMessage.get_client_server_message_type_class()

		print(f"{datetime.utcnow()}: test: client_server_message_type_class: {client_server_message_type_class}")

		self.assertIsNotNone(client_server_message_type_class)

		json_object = {"__type": "url_navigation_needed_response", "url": "https://www.google.com", "destination_uuid": "4ac80e82-5f0f-408a-8ed8-613570e3cb4f", "external_client_id": "4fdd847f-d4fe-4f41-99fe-b34a5ca59092"}

		client_server_message_type = client_server_message_type_class(json_object["__type"])

		print(f"{datetime.utcnow()}: test: client_server_message_type: {client_server_message_type}")

		self.assertIsNotNone(client_server_message_type)

		with self.assertRaises(KeyError):
			client_server_message_class = ClientAuthenticationClientServerMessage.get_client_server_message_class(
				client_server_message_type=GameManagerClientServerMessageTypeEnum.GameManagerError
			)

			print(f"{datetime.utcnow()}: test: client_server_message_class: {client_server_message_class}")

	def test_connect(self):

		server_messenger = get_default_server_messenger_factory().get_server_messenger()

		server_messenger.start_receiving_from_clients()

		client_messenger = get_default_client_messenger_factory().get_client_messenger()

		client_messenger.connect_to_server()

		time.sleep(1)

		client_messenger.dispose()

		time.sleep(1)

		server_messenger.stop_receiving_from_clients()

		server_messenger.dispose()

	def test_client_authentication(self):

		server_messenger = get_default_server_messenger_factory().get_server_messenger()

		server_messenger.start_receiving_from_clients()

		client_messenger = get_default_client_messenger_factory().get_client_messenger()

		client_messenger.connect_to_server()

		callback_total = 0
		authentication_response_client_server_message = None  # type: AuthenticateClientResponseGameManagerClientServerMessage
		blocking_semaphore = Semaphore()
		blocking_semaphore.acquire()

		def callback(client_server_message: GameManagerClientServerMessage):
			nonlocal callback_total
			nonlocal authentication_response_client_server_message

			callback_total += 1
			print(f"{datetime.utcnow()}: test: callback: client_server_message: {client_server_message.__class__.get_client_server_message_type()}")
			if callback_total == 1:
				self.assertIsInstance(client_server_message, UrlNavigationNeededResponseGameManagerClientServerMessage)
				client_server_message.navigate_to_url()
			elif callback_total == 2:
				self.assertIsInstance(client_server_message, AuthenticateClientResponseGameManagerClientServerMessage)
				authentication_response_client_server_message = client_server_message
				blocking_semaphore.release()
			else:
				raise Exception(f"Unexpected callback total: {callback_total}")

		found_exception = None

		def on_exception(exception: Exception):
			nonlocal found_exception
			if found_exception is None:
				found_exception = exception

		client_messenger.receive_from_server(
			callback=callback,
			on_exception=on_exception
		)

		client_messenger.send_to_server(
			request_client_server_message=AuthenticateClientRequestGameManagerClientServerMessage()
		)

		print(f"{datetime.utcnow()}: test: waiting for authentication: start")
		blocking_semaphore.acquire()
		blocking_semaphore.release()
		print(f"{datetime.utcnow()}: test: waiting for authentication: end")

		time.sleep(1)

		client_messenger.dispose()

		time.sleep(1)

		server_messenger.stop_receiving_from_clients()

		server_messenger.dispose()

		self.assertIsNotNone(authentication_response_client_server_message)
		self.assertTrue(authentication_response_client_server_message.is_successful())

	def test_multiple_client_authentication_sequential(self):

		time.sleep(1)

		server_messenger = get_default_server_messenger_factory().get_server_messenger()

		server_messenger.start_receiving_from_clients()

		time.sleep(1)

		client_messenger = get_default_client_messenger_factory().get_client_messenger()

		client_messenger.connect_to_server()

		callback_total = 0
		authentication_response_client_server_message = None  # type: AuthenticateClientResponseGameManagerClientServerMessage
		blocking_semaphore = Semaphore()
		blocking_semaphore.acquire()

		def callback(client_server_message: GameManagerClientServerMessage):
			nonlocal callback_total
			nonlocal authentication_response_client_server_message

			callback_total += 1
			print(f"{datetime.utcnow()}: test: callback: client_server_message: {client_server_message.__class__.get_client_server_message_type()}")
			if callback_total == 1:
				self.assertIsInstance(client_server_message, UrlNavigationNeededResponseGameManagerClientServerMessage)
				client_server_message.navigate_to_url()
			elif callback_total == 2:
				self.assertIsInstance(client_server_message, AuthenticateClientResponseGameManagerClientServerMessage)
				authentication_response_client_server_message = client_server_message
				blocking_semaphore.release()
			elif callback_total == 3:
				self.assertIsInstance(client_server_message, ClientAlreadyAuthenticatedErrorGameManagerClientServerMessage)
				blocking_semaphore.release()
			else:
				raise Exception(f"Unexpected callback total: {callback_total}")

		found_exception = None

		def on_exception(exception: Exception):
			print(f"GameManagerTest: test: exception: {exception}")
			nonlocal found_exception
			if found_exception is None:
				found_exception = exception

		client_messenger.receive_from_server(
			callback=callback,
			on_exception=on_exception
		)

		for index in range(2):
			client_messenger.send_to_server(
				request_client_server_message=AuthenticateClientRequestGameManagerClientServerMessage()
			)

			print(f"{datetime.utcnow()}: test: waiting for authentication: start")
			blocking_semaphore.acquire()
			print(f"{datetime.utcnow()}: test: waiting for authentication: end")

		blocking_semaphore.release()

		time.sleep(1)

		client_messenger.dispose()

		time.sleep(1)

		server_messenger.stop_receiving_from_clients()

		server_messenger.dispose()

		self.assertIsNotNone(authentication_response_client_server_message)
		self.assertTrue(authentication_response_client_server_message.is_successful())

	def test_multiple_client_authentication_parallel(self):

		clients_total = 2

		server_messenger = get_default_server_messenger_factory().get_server_messenger()

		server_messenger.start_receiving_from_clients()

		navigate_to_url_semaphore = Semaphore()
		callback_total = 0

		def client_messenger_thread_method():
			nonlocal navigate_to_url_semaphore
			nonlocal callback_total

			client_messenger = get_default_client_messenger_factory().get_client_messenger()

			client_messenger.connect_to_server()

			blocking_semaphore = Semaphore()
			blocking_semaphore.acquire()

			local_callback_total = 0

			def callback(client_server_message: GameManagerClientServerMessage):
				nonlocal callback_total
				nonlocal local_callback_total
				nonlocal navigate_to_url_semaphore

				callback_total += 1
				local_callback_total += 1
				print(f"{datetime.utcnow()}: test: callback: client_server_message: {client_server_message.__class__.get_client_server_message_type()}")
				if local_callback_total == 1:
					self.assertIsInstance(client_server_message, UrlNavigationNeededResponseGameManagerClientServerMessage)
					print(f"{datetime.utcnow()}: test: callback: navigating to url: {client_server_message.get_url()}")
					navigate_to_url_semaphore.acquire()
					client_server_message.navigate_to_url()
					time.sleep(1)
					navigate_to_url_semaphore.release()
				elif local_callback_total == 2:
					self.assertIsInstance(client_server_message, AuthenticateClientResponseGameManagerClientServerMessage)
					blocking_semaphore.release()
				else:
					raise Exception(f"Unexpected callback total: {callback_total}")

			found_exception = None

			def on_exception(exception: Exception):
				print(f"GameManagerTest: test: exception: {exception}")
				nonlocal found_exception
				if found_exception is None:
					found_exception = exception

			client_messenger.receive_from_server(
				callback=callback,
				on_exception=on_exception
			)

			client_messenger.send_to_server(
				request_client_server_message=AuthenticateClientRequestGameManagerClientServerMessage()
			)

			print(f"{datetime.utcnow()}: test: waiting for authentication: start")
			blocking_semaphore.acquire()
			print(f"{datetime.utcnow()}: test: waiting for authentication: end")

			blocking_semaphore.release()

			time.sleep(1)

			client_messenger.dispose()

		client_threads = []
		for client_index in range(clients_total):
			client_thread = start_thread(client_messenger_thread_method)
			client_threads.append(client_thread)

		time.sleep(1)

		for client_thread in client_threads:
			client_thread.join()

		server_messenger.stop_receiving_from_clients()

		server_messenger.dispose()

		self.assertEqual(4, callback_total)

	def test_multiple_client_authentication_parallel_but_first_disconnects(self):

		clients_total = 2

		server_messenger = get_default_server_messenger_factory().get_server_messenger()

		server_messenger.start_receiving_from_clients()

		navigate_to_url_semaphore = Semaphore()
		callback_total = 0

		def client_messenger_thread_method(client_index: int):
			nonlocal navigate_to_url_semaphore
			nonlocal callback_total

			client_messenger = get_default_client_messenger_factory().get_client_messenger()

			client_messenger.connect_to_server()

			blocking_semaphore = Semaphore()
			blocking_semaphore.acquire()

			local_callback_total = 0

			def callback(client_server_message: GameManagerClientServerMessage):
				nonlocal callback_total
				nonlocal local_callback_total
				nonlocal navigate_to_url_semaphore
				nonlocal client_messenger

				callback_total += 1
				local_callback_total += 1
				print(f"{datetime.utcnow()}: test: callback: client_server_message: {client_server_message.__class__.get_client_server_message_type()}")
				if local_callback_total == 1:
					self.assertIsInstance(client_server_message, UrlNavigationNeededResponseGameManagerClientServerMessage)
					print(f"{datetime.utcnow()}: test: callback: navigating to url: {client_server_message.get_url()}")
					navigate_to_url_semaphore.acquire()
					client_server_message.navigate_to_url()
					time.sleep(1)
					navigate_to_url_semaphore.release()
					if client_index == 0:
						print(f"{datetime.utcnow()}: test: disposing client: start")
						client_messenger.dispose()
						print(f"{datetime.utcnow()}: test: disposing client: end")
						blocking_semaphore.release()
				elif local_callback_total == 2 and client_index != 0:
					self.assertIsInstance(client_server_message, AuthenticateClientResponseGameManagerClientServerMessage)
					blocking_semaphore.release()
				else:
					raise Exception(f"Unexpected callback total: {callback_total}")

			found_exception = None

			def on_exception(exception: Exception):
				print(f"GameManagerTest: test: exception: {exception}")
				nonlocal found_exception
				if found_exception is None:
					found_exception = exception

			client_messenger.receive_from_server(
				callback=callback,
				on_exception=on_exception
			)

			client_messenger.send_to_server(
				request_client_server_message=AuthenticateClientRequestGameManagerClientServerMessage()
			)

			print(f"{datetime.utcnow()}: test: waiting for authentication: start")
			blocking_semaphore.acquire()
			print(f"{datetime.utcnow()}: test: waiting for authentication: end")

			blocking_semaphore.release()

			time.sleep(1)

			if client_index != 0:
				client_messenger.dispose()

		client_threads = []
		for client_index in range(clients_total):
			client_thread = start_thread(client_messenger_thread_method, client_index)
			client_threads.append(client_thread)

		time.sleep(1)

		for client_thread in client_threads:
			client_thread.join()

		server_messenger.stop_receiving_from_clients()

		server_messenger.dispose()

		self.assertEqual(3, callback_total)
