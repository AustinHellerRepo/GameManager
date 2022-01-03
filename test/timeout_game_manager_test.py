from __future__ import annotations
import unittest
from typing import List, Tuple, Dict, Callable, Type, Set
import os
import time
from datetime import datetime
import uuid
from src.austin_heller_repo.game_manager import GameManagerClientServerMessage, GameManagerStructureFactory, AuthenticateClientRequestGameManagerClientServerMessage, AuthenticateClientResponseGameManagerClientServerMessage, UrlNavigationNeededResponseGameManagerClientServerMessage, GameManagerClientServerMessageTypeEnum, ClientAlreadyAuthenticatedErrorGameManagerClientServerMessage, AuthenticationTimeoutErrorGameManagerClientServerMessage
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
			authentication_timeout_seconds=5,
			is_debug=True
		),
		is_debug=True
	)


class TimeoutGameManagerTest(unittest.TestCase):

	def test_client_authentication(self):

		server_messenger = get_default_server_messenger_factory().get_server_messenger()

		server_messenger.start_receiving_from_clients()

		client_messenger = get_default_client_messenger_factory().get_client_messenger()

		client_messenger.connect_to_server()

		callback_total = 0
		authentication_timeout_error_client_server_message = None  # type: AuthenticationTimeoutErrorGameManagerClientServerMessage
		blocking_semaphore = Semaphore()
		blocking_semaphore.acquire()

		def callback(client_server_message: GameManagerClientServerMessage):
			nonlocal callback_total
			nonlocal authentication_timeout_error_client_server_message

			callback_total += 1
			print(f"{datetime.utcnow()}: test: callback: client_server_message: {client_server_message.__class__.get_client_server_message_type()}")
			if callback_total == 1:
				self.assertIsInstance(client_server_message, UrlNavigationNeededResponseGameManagerClientServerMessage)
				client_server_message.navigate_to_url()
			elif callback_total == 2:
				self.assertIsInstance(client_server_message, AuthenticationTimeoutErrorGameManagerClientServerMessage)
				authentication_timeout_error_client_server_message = client_server_message
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

		print(f"WAIT UNTIL TOLD TO AUTHENTICATE")

		client_messenger.send_to_server(
			request_client_server_message=AuthenticateClientRequestGameManagerClientServerMessage()
		)

		print(f"{datetime.utcnow()}: test: waiting for authentication: start")
		blocking_semaphore.acquire()
		blocking_semaphore.release()
		print(f"{datetime.utcnow()}: test: waiting for authentication: end")

		print(f"AUTHENTICATE NOW")

		time.sleep(5)

		client_messenger.dispose()

		time.sleep(1)

		server_messenger.stop_receiving_from_clients()

		server_messenger.dispose()

		self.assertIsNotNone(authentication_timeout_error_client_server_message)
		self.assertEqual(2, callback_total)
