from __future__ import annotations
from typing import List, Tuple, Dict, Callable, Type, Set
import os
import tempfile
import time
import json
from datetime import datetime
import uuid
from abc import ABC, abstractmethod
import webbrowser
from austin_heller_repo.socket_queued_message_framework import ClientServerMessage, Structure, StructureStateEnum, ClientServerMessageTypeEnum, ClientMessengerFactory, StructureFactory, StructureInfluence, StructureTransitionException, ClientMessenger
from austin_heller_repo.client_authentication_manager import OpenidAuthenticationRequestClientAuthenticationClientServerMessage, AuthenticationResponseClientAuthenticationClientServerMessage, UrlNavigationNeededResponseClientAuthenticationClientServerMessage, UnexpectedAuthenticationRequestClientAuthenticationClientServerMessage, UnexpectedOpenidAuthenticationResponseClientAuthenticationClientServerMessage
from austin_heller_repo.threading import Semaphore, start_thread


class GameManagerStructureStateEnum(StructureStateEnum):
	Active = "active"
	UnderMaintenance = "under_maintenance"


class GameManagerClientServerMessageTypeEnum(ClientServerMessageTypeEnum):
	GameManagerError = "game_manager_error"
	AuthenticateClientRequest = "authenticate_client_request"
	UrlNavigationNeededResponse = "url_navigation_needed_response"
	AuthenticateClientResponse = "authenticate_client_response"
	AuthenticationTimeoutError = "authentication_timeout_error"
	ClientAlreadyAuthenticatedError = "client_already_authenticated_error"
	ClientAuthenticationManagerError = "client_authentication_manager_error"


class GameManagerClientServerMessage(ClientServerMessage, ABC):

	def __init__(self):
		super().__init__()

		pass

	@classmethod
	def get_client_server_message_type_class(cls) -> Type[ClientServerMessageTypeEnum]:
		return GameManagerClientServerMessageTypeEnum


class GameManagerErrorGameManagerClientServerMessage(GameManagerClientServerMessage):

	def __init__(self, *, structure_state_name: str, client_server_message_json_string: str, destination_uuid: str):
		super().__init__()

		self.__structure_state_name = structure_state_name
		self.__client_server_message_json_string = client_server_message_json_string
		self.__destination_uuid = destination_uuid

	def get_structure_state(self) -> GameManagerStructureStateEnum:
		return GameManagerStructureStateEnum(self.__structure_state_name)

	def get_client_server_message(self) -> GameManagerClientServerMessage:
		return GameManagerClientServerMessage.parse_from_json(
			json_object=json.loads(self.__client_server_message_json_string)
		)

	@classmethod
	def get_client_server_message_type(cls) -> ClientServerMessageTypeEnum:
		return GameManagerClientServerMessageTypeEnum.GameManagerError

	def to_json(self) -> Dict:
		json_object = super().to_json()
		json_object["structure_state_name"] = self.__structure_state_name
		json_object["client_server_message_json_string"] = self.__client_server_message_json_string
		json_object["destination_uuid"] = self.__destination_uuid
		return json_object

	def is_response(self) -> bool:
		return True

	def get_destination_uuid(self) -> str:
		return self.__destination_uuid

	def is_structural_influence(self) -> bool:
		return False

	def is_ordered(self) -> bool:
		return True

	def get_structural_error_client_server_message_response(self, *, structure_transition_exception: StructureTransitionException, destination_uuid: str) -> ClientServerMessage:
		return None


class AuthenticateClientRequestGameManagerClientServerMessage(GameManagerClientServerMessage):

	def __init__(self):
		super().__init__()

		pass

	@classmethod
	def get_client_server_message_type(cls) -> ClientServerMessageTypeEnum:
		return GameManagerClientServerMessageTypeEnum.AuthenticateClientRequest

	def to_json(self) -> Dict:
		json_object = super().to_json()
		return json_object

	def is_response(self) -> bool:
		return False

	def get_destination_uuid(self) -> str:
		return None

	def is_structural_influence(self) -> bool:
		return True

	def is_ordered(self) -> bool:
		return True

	def get_structural_error_client_server_message_response(self, *, structure_transition_exception: StructureTransitionException, destination_uuid: str) -> ClientServerMessage:
		return GameManagerErrorGameManagerClientServerMessage(
			structure_state_name=structure_transition_exception.get_structure_state().value,
			client_server_message_json_string=json.dumps(structure_transition_exception.get_structure_influence().get_client_server_message().to_json()),
			destination_uuid=destination_uuid
		)


class UrlNavigationNeededResponseGameManagerClientServerMessage(GameManagerClientServerMessage):

	def __init__(self, *, url: str, destination_uuid: str):
		super().__init__()

		self.__url = url
		self.__destination_uuid = destination_uuid

	def get_url(self) -> str:
		return self.__url

	def navigate_to_url(self):
		webbrowser.open(self.__url, new=2)

	@classmethod
	def get_client_server_message_type(cls) -> ClientServerMessageTypeEnum:
		return GameManagerClientServerMessageTypeEnum.UrlNavigationNeededResponse

	def to_json(self) -> Dict:
		json_object = super().to_json()
		json_object["url"] = self.__url
		json_object["destination_uuid"] = self.__destination_uuid
		return json_object

	def is_response(self) -> bool:
		return True

	def get_destination_uuid(self) -> str:
		return self.__destination_uuid

	def is_structural_influence(self) -> bool:
		return False

	def is_ordered(self) -> bool:
		return True

	def get_structural_error_client_server_message_response(self, *, structure_transition_exception: StructureTransitionException, destination_uuid: str) -> ClientServerMessage:
		return GameManagerErrorGameManagerClientServerMessage(
			structure_state_name=structure_transition_exception.get_structure_state().value,
			client_server_message_json_string=json.dumps(structure_transition_exception.get_structure_influence().get_client_server_message().to_json()),
			destination_uuid=destination_uuid
		)


class AuthenticateClientResponseGameManagerClientServerMessage(GameManagerClientServerMessage):

	def __init__(self, *, is_successful: bool, destination_uuid: str):
		super().__init__()

		self.__is_successful = is_successful
		self.__destination_uuid = destination_uuid

	def is_successful(self) -> bool:
		return self.__is_successful

	@classmethod
	def get_client_server_message_type(cls) -> ClientServerMessageTypeEnum:
		return GameManagerClientServerMessageTypeEnum.AuthenticateClientResponse

	def to_json(self) -> Dict:
		json_object = super().to_json()
		json_object["is_successful"] = self.__is_successful
		json_object["destination_uuid"] = self.__destination_uuid
		return json_object

	def is_response(self) -> bool:
		return True

	def get_destination_uuid(self) -> str:
		return self.__destination_uuid

	def is_structural_influence(self) -> bool:
		return False

	def is_ordered(self) -> bool:
		return True

	def get_structural_error_client_server_message_response(self, *, structure_transition_exception: StructureTransitionException, destination_uuid: str) -> ClientServerMessage:
		return GameManagerErrorGameManagerClientServerMessage(
			structure_state_name=structure_transition_exception.get_structure_state().value,
			client_server_message_json_string=json.dumps(structure_transition_exception.get_structure_influence().get_client_server_message().to_json()),
			destination_uuid=destination_uuid
		)


class AuthenticationTimeoutErrorGameManagerClientServerMessage(GameManagerClientServerMessage):

	def __init__(self, *, destination_uuid: str):
		super().__init__()

		self.__destination_uuid = destination_uuid

	@classmethod
	def get_client_server_message_type(cls) -> ClientServerMessageTypeEnum:
		return GameManagerClientServerMessageTypeEnum.AuthenticationTimeoutError

	def to_json(self) -> Dict:
		json_object = super().to_json()
		json_object["destination_uuid"] = self.__destination_uuid
		return json_object

	def is_response(self) -> bool:
		return True

	def get_destination_uuid(self) -> str:
		return self.__destination_uuid

	def is_structural_influence(self) -> bool:
		return False

	def is_ordered(self) -> bool:
		return True

	def get_structural_error_client_server_message_response(self, *, structure_transition_exception: StructureTransitionException, destination_uuid: str) -> ClientServerMessage:
		return None


class ClientAlreadyAuthenticatedErrorGameManagerClientServerMessage(GameManagerClientServerMessage):

	def __init__(self, *, destination_uuid: str):
		super().__init__()

		self.__destination_uuid = destination_uuid

	@classmethod
	def get_client_server_message_type(cls) -> ClientServerMessageTypeEnum:
		return GameManagerClientServerMessageTypeEnum.ClientAlreadyAuthenticatedError

	def to_json(self) -> Dict:
		json_object = super().to_json()
		json_object["destination_uuid"] = self.__destination_uuid
		return json_object

	def is_response(self) -> bool:
		return True

	def get_destination_uuid(self) -> str:
		return self.__destination_uuid

	def is_structural_influence(self) -> bool:
		return False

	def is_ordered(self) -> bool:
		return True

	def get_structural_error_client_server_message_response(self, *, structure_transition_exception: StructureTransitionException, destination_uuid: str) -> ClientServerMessage:
		return None


class ClientAuthenticationManagerErrorGameManagerClientServerMessage(GameManagerClientServerMessage):

	def __init__(self, *, message: str, destination_uuid: str):
		super().__init__()

		self.__message = message
		self.__destination_uuid = destination_uuid

	def get_message(self) -> str:
		return self.__message

	@classmethod
	def get_client_server_message_type(cls) -> ClientServerMessageTypeEnum:
		return GameManagerClientServerMessageTypeEnum.ClientAuthenticationManagerError

	def to_json(self) -> Dict:
		json_object = super().to_json()
		json_object["message"] = self.__message
		json_object["destination_uuid"] = self.__destination_uuid
		return json_object

	def is_response(self) -> bool:
		return True

	def get_destination_uuid(self) -> str:
		return self.__destination_uuid

	def is_structural_influence(self) -> bool:
		return False

	def is_ordered(self) -> bool:
		return True

	def get_structural_error_client_server_message_response(self, *, structure_transition_exception: StructureTransitionException, destination_uuid: str) -> ClientServerMessage:
		return None


class GameManagerStructure(Structure):

	def __init__(self, *, client_authentication_client_messenger_factory: ClientMessengerFactory, authentication_timeout_seconds: float, is_debug: bool = False):
		super().__init__(
			states=GameManagerStructureStateEnum,
			initial_state=GameManagerStructureStateEnum.Active  # TODO start UnderMaintenance
		)

		self.__client_authentication_client_messenger_factory = client_authentication_client_messenger_factory
		self.__authentication_timeout_seconds = authentication_timeout_seconds
		self.__is_debug = is_debug

		self.__client_authentication_client_messenger = None  # type: ClientMessenger
		self.__authentication_id_per_client_uuid = {}  # type: Dict[str, str]
		self.__authentication_id_per_client_uuid_semaphore = Semaphore()
		self.__found_exception = None  # type: Exception
		self.__authentication_uuids = set()  # type: Set[str]
		self.__authentication_uuids_semaphore = Semaphore()

		self.add_transition(
			client_server_message_type=GameManagerClientServerMessageTypeEnum.AuthenticateClientRequest,
			start_structure_state=GameManagerStructureStateEnum.Active,
			end_structure_state=GameManagerStructureStateEnum.Active,
			on_transition=self.__authenticate_client_request_received
		)

		self.__initialize()

	def __initialize(self):

		self.__client_authentication_client_messenger = self.__client_authentication_client_messenger_factory.get_client_messenger()

		self.__client_authentication_client_messenger.connect_to_server()

		self.__client_authentication_client_messenger.receive_from_server(
			callback=self.__client_authentication_client_messenger_callback,
			on_exception=self.__client_authentication_client_messenger_on_exception
		)

	def __client_authentication_client_messenger_callback(self, client_server_message: ClientServerMessage):
		print(f"{datetime.utcnow()}: GameManagerStructure: __client_authentication_client_messenger_callback: client_server_message: {client_server_message}")
		if isinstance(client_server_message, UrlNavigationNeededResponseClientAuthenticationClientServerMessage):
			external_metadata_json = client_server_message.get_external_metadata_json()
			self.__authentication_uuids_semaphore.acquire()
			if external_metadata_json["authentication_uuid"] in self.__authentication_uuids:
				self.__authentication_uuids_semaphore.release()
				self.send_response(
					client_server_message=UrlNavigationNeededResponseGameManagerClientServerMessage(
						url=client_server_message.get_url(),
						destination_uuid=external_metadata_json["client_uuid"]
					)
				)
			else:
				if self.__is_debug:
					print(f"{datetime.utcnow()}: GameManagerStructure: __client_authentication_client_messenger_callback: UrlNavigationNeededResponseClientAuthenticationClientServerMessage: authentication_uuid missing")
				self.__authentication_uuids_semaphore.release()
		elif isinstance(client_server_message, AuthenticationResponseClientAuthenticationClientServerMessage):
			external_metadata_json = client_server_message.get_external_metadata_json()
			self.__authentication_uuids_semaphore.acquire()
			if external_metadata_json["authentication_uuid"] in self.__authentication_uuids:
				self.__authentication_uuids.remove(external_metadata_json["authentication_uuid"])
				self.__authentication_uuids_semaphore.release()

				self.__authentication_id_per_client_uuid_semaphore.acquire()
				if external_metadata_json["client_uuid"] in self.__authentication_id_per_client_uuid:
					self.__authentication_id_per_client_uuid_semaphore.release()
					self.send_response(
						client_server_message=ClientAlreadyAuthenticatedErrorGameManagerClientServerMessage(
							destination_uuid=external_metadata_json["client_uuid"]
						)
					)
				else:
					if client_server_message.is_successful():
						self.__authentication_id_per_client_uuid[external_metadata_json["client_uuid"]] = client_server_message.get_authentication_id()
					self.__authentication_id_per_client_uuid_semaphore.release()
					self.send_response(
						client_server_message=AuthenticateClientResponseGameManagerClientServerMessage(
							is_successful=client_server_message.is_successful(),
							destination_uuid=external_metadata_json["client_uuid"]
						)
					)
			else:
				if self.__is_debug:
					print(f"{datetime.utcnow()}: GameManagerStructure: __client_authentication_client_messenger_callback: AuthenticationResponseClientAuthenticationClientServerMessage: authentication_uuid missing")
				self.__authentication_uuids_semaphore.release()
		elif isinstance(client_server_message, UnexpectedAuthenticationRequestClientAuthenticationClientServerMessage):
			external_metadata_json = client_server_message.get_external_metadata_json()
			self.send_response(
				client_server_message=ClientAuthenticationManagerErrorGameManagerClientServerMessage(
					message=f"Unexpected authentication request {client_server_message.get_client_server_message().__class__.get_client_server_message_type()} while in state {client_server_message.get_structure_state().value}",
					destination_uuid=external_metadata_json["client_uuid"]
				)
			)
		elif isinstance(client_server_message, UnexpectedOpenidAuthenticationResponseClientAuthenticationClientServerMessage):
			print(f"Received OpenID Connect response unexpectedly as {client_server_message.get_client_server_message().__class__.get_client_server_message_type()} while in state {client_server_message.get_structure_state().value}")
		else:
			raise Exception(f"{datetime.utcnow()}: GameManagerStructure: __client_authentication_client_messenger_callback: Unexpected ClientAuthenticationClientServerMessage: {type(client_server_message)}.")

	def __client_authentication_client_messenger_on_exception(self, exception: Exception):
		print(f"{datetime.utcnow()}: GameManagerStructure: __client_authentication_client_messenger_on_exception: exception: {exception}")
		if self.__found_exception is None:
			self.__found_exception = exception

	def __authenticate_client_request_received(self, structure_influence: StructureInfluence):

		openid_authentication_request = structure_influence.get_client_server_message()  # type: AuthenticateClientRequestGameManagerClientServerMessage

		client_uuid = structure_influence.get_source_uuid()

		if client_uuid in self.__authentication_id_per_client_uuid:
			self.send_response(
				client_server_message=ClientAlreadyAuthenticatedErrorGameManagerClientServerMessage(
					destination_uuid=client_uuid
				)
			)
		else:
			external_metadata_json = {
				"client_uuid": client_uuid,
				"authentication_uuid": str(uuid.uuid4())
			}
			self.__authentication_uuids_semaphore.acquire()
			self.__authentication_uuids.add(external_metadata_json["authentication_uuid"])
			self.__authentication_uuids_semaphore.release()
			self.__client_authentication_client_messenger.send_to_server(
				request_client_server_message=OpenidAuthenticationRequestClientAuthenticationClientServerMessage(
					external_metadata_json=external_metadata_json
				)
			)

			def timeout_thread():
				nonlocal external_metadata_json

				if self.__is_debug:
					print(f"GameManagerStructure: __authenticate_client_request_received: timeout_thread: time.sleep: start")
				time.sleep(self.__authentication_timeout_seconds)
				if self.__is_debug:
					print(f"GameManagerStructure: __authenticate_client_request_received: timeout_thread: time.sleep: end")

				self.__authentication_uuids_semaphore.acquire()
				if external_metadata_json["authentication_uuid"] in self.__authentication_uuids:
					is_timeout = True
					self.__authentication_uuids.remove(external_metadata_json["authentication_uuid"])
				else:
					is_timeout = False
				self.__authentication_uuids_semaphore.release()

				if is_timeout:
					if self.__is_debug:
						print(f"GameManagerStructure: __authenticate_client_request_received: timeout_thread: send_response: start")
					self.send_response(
						client_server_message=AuthenticationTimeoutErrorGameManagerClientServerMessage(
							destination_uuid=external_metadata_json["client_uuid"]
						)
					)
					if self.__is_debug:
						print(f"GameManagerStructure: __authenticate_client_request_received: timeout_thread: send_response: end")

			start_thread(timeout_thread)

	def dispose(self):
		self.__client_authentication_client_messenger.dispose()


class GameManagerStructureFactory(StructureFactory):

	def __init__(self, *, client_authentication_client_messenger_factory: ClientMessengerFactory, authentication_timeout_seconds: float, is_debug: bool = False):

		self.__client_authentication_client_messenger_factory = client_authentication_client_messenger_factory
		self.__authentication_timeout_seconds = authentication_timeout_seconds
		self.__is_debug = is_debug

	def get_structure(self) -> Structure:
		return GameManagerStructure(
			client_authentication_client_messenger_factory=self.__client_authentication_client_messenger_factory,
			authentication_timeout_seconds=self.__authentication_timeout_seconds,
			is_debug=self.__is_debug
		)
