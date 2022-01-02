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
from austin_heller_repo.threading import Semaphore


class GameManagerStructureStateEnum(StructureStateEnum):
	Active = "active"
	UnderMaintenance = "under_maintenance"


class GameManagerClientServerMessageTypeEnum(ClientServerMessageTypeEnum):
	UnexpectedGameManagerRequest = "unexpected_game_manager_request"
	AuthenticateClientRequest = "authenticate_client_request"
	UrlNavigationNeededResponse = "url_navigation_needed_response"
	AuthenticateClientResponse = "authenticate_client_response"
	AuthenticationExceptionResponse = "authentication_exception_response"


class GameManagerClientServerMessage(ClientServerMessage, ABC):

	def __init__(self):
		super().__init__()

		pass

	@classmethod
	def get_client_server_message_type_class(cls) -> Type[ClientServerMessageTypeEnum]:
		return GameManagerClientServerMessageTypeEnum


class UnexpectedGameManagerRequestGameManagerClientServerMessage(GameManagerClientServerMessage):

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
		return GameManagerClientServerMessageTypeEnum.UnexpectedGameManagerRequest

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
		return UnexpectedGameManagerRequestGameManagerClientServerMessage(
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
		return UnexpectedGameManagerRequestGameManagerClientServerMessage(
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
		return UnexpectedGameManagerRequestGameManagerClientServerMessage(
			structure_state_name=structure_transition_exception.get_structure_state().value,
			client_server_message_json_string=json.dumps(structure_transition_exception.get_structure_influence().get_client_server_message().to_json()),
			destination_uuid=destination_uuid
		)


class AuthenticationExceptionResponseGameManagerClientServerMessage(GameManagerClientServerMessage):

	def __init__(self, *, exception_message: str, destination_uuid: str):
		super().__init__()

		self.__exception_message = exception_message
		self.__destination_uuid = destination_uuid

	def get_exception_message(self) -> str:
		return self.__exception_message

	@classmethod
	def get_client_server_message_type(cls) -> ClientServerMessageTypeEnum:
		return GameManagerClientServerMessageTypeEnum.AuthenticationExceptionResponse

	def to_json(self) -> Dict:
		json_object = super().to_json()
		json_object["exception_message"] = self.__exception_message
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

	def __init__(self, *, client_authentication_client_messenger_factory: ClientMessengerFactory):
		super().__init__(
			states=GameManagerStructureStateEnum,
			initial_state=GameManagerStructureStateEnum.Active  # TODO start UnderMaintenance
		)

		self.__client_authentication_client_messenger_factory = client_authentication_client_messenger_factory

		# TODO add dispose method to Structure and to ServerMessenger (so that it can call dispose on internal structures)
		self.__client_authentication_client_messenger = None  # type: ClientMessenger
		self.__authentication_id_per_client_uuid = {}  # type: Dict[str, str]
		self.__authentication_id_per_client_uuid_semaphore = Semaphore()
		self.__found_exception = None  # type: Exception

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
			external_client_id = client_server_message.get_external_client_id()
			self.send_response(
				client_server_message=UrlNavigationNeededResponseGameManagerClientServerMessage(
					url=client_server_message.get_url(),
					destination_uuid=external_client_id
				)
			)
		elif isinstance(client_server_message, AuthenticationResponseClientAuthenticationClientServerMessage):
			external_client_id = client_server_message.get_external_client_id()
			if client_server_message.is_successful():
				self.__authentication_id_per_client_uuid_semaphore.acquire()
				self.__authentication_id_per_client_uuid[external_client_id] = client_server_message.get_authentication_id()
				self.__authentication_id_per_client_uuid_semaphore.release()
			self.send_response(
				client_server_message=AuthenticateClientResponseGameManagerClientServerMessage(
					is_successful=client_server_message.is_successful(),
					destination_uuid=external_client_id
				)
			)
		elif isinstance(client_server_message, UnexpectedAuthenticationRequestClientAuthenticationClientServerMessage):
			external_client_id = client_server_message.get_external_client_id()
			self.send_response(
				client_server_message=AuthenticationExceptionResponseGameManagerClientServerMessage(
					exception_message=f"Unexpected authentication request {client_server_message.get_client_server_message().__class__.get_client_server_message_type()} while in state {client_server_message.get_structure_state().value}",
					destination_uuid=external_client_id
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

		external_client_id = structure_influence.get_source_uuid()

		self.__client_authentication_client_messenger.send_to_server(
			request_client_server_message=OpenidAuthenticationRequestClientAuthenticationClientServerMessage(
				external_client_id=external_client_id
			)
		)

	def dispose(self):
		self.__client_authentication_client_messenger.dispose()


class GameManagerStructureFactory(StructureFactory):

	def __init__(self, *, client_authentication_client_messenger_factory: ClientMessengerFactory):

		self.__client_authentication_client_messenger_factory = client_authentication_client_messenger_factory

	def get_structure(self) -> Structure:
		return GameManagerStructure(
			client_authentication_client_messenger_factory=self.__client_authentication_client_messenger_factory
		)
