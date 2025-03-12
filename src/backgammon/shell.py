# Copyright 2020 Softwerks LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import cmd
import os
import re
import threading
import traceback
from datetime import datetime
from getpass import getpass
from json import dumps, loads, dump
from typing import List, Optional, Tuple, Union, cast

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from jose import jwt

import websocket
from stonesandice.board import Board
from stonesandice.logger import logger
from stonesandice.models import MatchPutRequest, MatchPostRequest
from stonesandice.utils import str_to_class

try:
    import readline
except ImportError:
    pass

import tables
from stonesandice.board import BoardError
from stonesandice.match import GameState, Resign
from stonesandice.player import Player, PlayerType
from stonesandice.variants.backgammon import Backgammon
from stonesandice.models import UserType

# System settings
file_path: str = (
    f"{os.path.dirname(__file__)}/match.json"
    if os.path.dirname(__file__) != ""
    else "match.json"
)


class Shell(cmd.Cmd):
    # Cmd Settings
    intro: str = "Type 'help' or '?' to list commands."
    prompt: str = "stones+dice> "

    # Backgammon settings
    game: Backgammon = None
    match: dict = None
    player0: dict = None
    player1: dict = None
    is_local: bool = None

    # Cognito settings
    client_id: str = "1s1didmskm45b8ks9na00praf4"
    userpool_id: str = "eu-west-1_vHKfvuAiC"
    identity_pool_id: str = "eu-west-1:87c96ea4-3896-4ba9-b66d-b9d641dc434c"
    region: str = "eu-west-1"
    account_id: str = "093581297635"
    service: str = "execute-api"
    credentials: dict = None
    identity_id = None
    jwt_access_token: str = ""
    jwt_id_token: str = ""
    jwt_refresh_token: str = ""
    claims: dict = {}
    player_id: str = ""
    username: str = ""
    user_attributes: dict = {}
    opponent: Player = None

    # Websocket settings
    websocket_url = "wss://websocket.stonesandice.com/"
    match_ref: str = ""
    _websocket = None

    def __init__(self):
        super().__init__()
        self.idp_client = boto3.client("cognito-idp", region_name=self.region)
        self.identity_client = boto3.client("cognito-identity", region_name=self.region)
        self.login_path = f"cognito-idp.{self.region}.amazonaws.com/{self.userpool_id}"

    @property
    def websocket(self):
        return self._websocket

    # CMD FUNCTIONS

    def cmdloop(self, intro=None):
        """

        Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.
        """

        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline

                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey + ": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = input(self.prompt)
                        except EOFError:
                            line = "EOF"
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = "EOF"
                        else:
                            line = line.rstrip("\r\n")
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline

                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    def onecmd(self, line):
        """

        Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)

        # Custom clause to check if it's a players turn
        if (
            self.game is not None
            and cmd
            in [
                "move",
                "roll",
                "double",
                "redouble",
                "reject",
                "accept",
                "take",
                "drop",
                "resign",
            ]
            and not self._your_turn()
        ):
            print(f"Cannot {cmd}: it's not your turn.")
            return

        # load the match
        if self.is_local:
            self._load_match()

        self.lastcmd = line
        if line == "EOF":
            self.lastcmd = ""
        if cmd == "":
            return self.default(line)
        else:
            try:
                func = getattr(self, "do_" + cmd)
            except AttributeError:
                return self.default(line)
            return func(arg)

    # SHELL COMMANDS

    # Cognito Auth

    def do_signup(self, arg: str) -> None:
        """Signup new player"""
        nickname = input("Nickname: ")
        email = input("Email: ")
        password = getpass("Password: ")
        try:
            self.idp_client.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {
                        "Name": "email",
                        "Value": email,
                    },
                    {
                        "Name": "nickname",
                        "Value": nickname,
                    },
                    {
                        "Name": "custom:userType",
                        "Value": UserType.HumanPlayer.name,
                    },
                ],
            )
            print("Check your email for a verification link.")
        except Exception as exc:
            print(exc)

    def do_login(self, arg: str) -> None:
        """login player"""
        email = input("Email: ")
        password = getpass("Password: ")
        try:
            response = self.idp_client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "EMAIL": email,
                    "PASSWORD": password,
                },
                ClientId=self.client_id,
            )
            self.jwt_access_token = response["AuthenticationResult"]["AccessToken"]
            self.jwt_id_token = response["AuthenticationResult"]["IdToken"]
            self.jwt_refresh_token = response["AuthenticationResult"]["RefreshToken"]
            self.claims = self._get_unverified_claims()
            self.credentials = self._get_credentials()
            self._get_user()
            self._create_websocket()
            threading.Thread(
                target=self._receive,
                name="Receive",
            ).start()
        except Exception as exc:
            print(exc)

    # Game commands

    def do_new(self, arg: str) -> None:
        """Start a match"""
        try:
            # Don't send a create match if a game has already started
            if hasattr(self, "game") and self.game is not None:
                return

            if self.credentials is None:
                print("Please login to continue...")
                return

            def prompt_user_for_parameter(parameter_name):
                value = input(f"Enter the value for {parameter_name}: ")
                return value

            def configure_backgammon_game():
                """
                {
                  "matchLength": 15,
                  "gameType": "Backgammon",
                  "crawford": true,
                  "autoDoubles": true,
                  "beavers": true,
                  "jacoby": true,
                  "bet": 2500,
                  "aceyDeucy": true
                }
                Returns:

                """
                parameters = {}

                parameters["matchLength"] = (
                    0  # prompt_user_for_parameter('match length')
                )
                parameters["gameType"] = (
                    "Backgammon"  # prompt_user_for_parameter('game type')
                )
                parameters["crawford"] = (
                    False  # prompt_user_for_parameter('crawford rule')
                )
                parameters["autoDoubles"] = (
                    True  # prompt_user_for_parameter('auto doubles')
                )
                parameters["beavers"] = True  # prompt_user_for_parameter('beavers')
                parameters["jacoby"] = True  # prompt_user_for_parameter('jacoby rule')
                parameters["bet"] = prompt_user_for_parameter("amount to bet")
                parameters["aceyDeucy"] = (
                    False  # prompt_user_for_parameter('acey deucy')
                )

                return parameters

            def save_parameters_to_json(parameters):
                with open("backgammon_parameters.json", "w") as file:
                    dump(parameters, file, indent=4)

            game_parameters = configure_backgammon_game()
            # save_parameters_to_json(game_parameters)

            match_post_request = loads(
                MatchPostRequest(**game_parameters).json(exclude_none=True)
            )

            print("Finding a match, please wait...")

            # Send the payload to the websocket
            threading.Thread(
                target=self._send, name="Send", args=("match", match_post_request)
            ).start()
            return
        except Exception as exc:
            print(exc)

    def do_roll(self, arg: str) -> None:
        """Creates a roll action"""
        try:
            if (
                self.game is not None
                and self.game.match.game_state == GameState.ON_ROLL
            ):
                self._send_update(action="roll")
            else:
                self.do_hint(arg="roll")
        except Exception as exc:
            print(exc)

    def do_double(self, arg: str) -> None:
        """Creates a double action"""
        try:
            if (
                self.game is not None
                and self.game.match.game_state == GameState.ON_ROLL
            ):
                self._send_update(action="double")
            else:
                self.do_hint(arg="double")
        except Exception as exc:
            print(exc)

    def do_redouble(self, arg: str) -> None:
        """Creates a redouble action"""
        try:
            if (
                self.game is not None
                and self.game.match.game_state == GameState.DOUBLED
            ):
                self._send_update(action="beaver")
            else:
                self.do_hint(arg="redouble")
        except Exception as exc:
            print(exc)

    def do_take(self, arg: str) -> None:
        """Takes a double"""
        try:
            if (
                self.game is not None
                and self.game.match.game_state == GameState.DOUBLED
            ):
                self._send_update(action="take")
            else:
                self.do_hint(arg="take")
        except Exception as exc:
            print(exc)

    def do_accept(self, arg: str) -> None:
        """Accepts a resignation"""
        try:
            if (
                self.game is not None
                and self.game.match.game_state == GameState.RESIGNED
            ):
                self._send_update(action="accept")
            else:
                self.do_hint(arg="accept")
        except Exception as exc:
            print(exc)

    def do_reject(self, arg: str) -> None:
        """Rejects a resignation"""
        try:
            if (
                self.game is not None
                and self.game.match.game_state == GameState.RESIGNED
            ):
                self._send_update(action="reject")
            else:
                self.do_hint(arg="reject")
        except Exception as exc:
            print(exc)

    def do_drop(self, arg: str) -> None:
        """Drops a cube"""
        try:
            if (
                self.game is not None
                and self.game.match.game_state == GameState.DOUBLED
            ):
                self._send_update(action="drop")
            else:
                self.do_hint(arg="drop")
        except Exception as exc:
            print(exc)

    def do_move(self, arg: str) -> None:
        """Make a backgammon move: move <from> <to> ..."""
        Moves = Tuple[Tuple[Optional[int], Optional[int]], ...]

        def parse_arg(arg: str) -> Moves:
            arg_ints: List[Optional[int]] = list(
                map(lambda n: (int(n) - 1) if n.isdigit() else -1, arg.split())
            )

            if len(arg_ints) % 2 == 1:
                raise ValueError("Incomplete move.")
            if len(arg_ints) > 8:
                raise ValueError("Too many moves.")

            return cast(
                Moves,
                tuple(tuple(arg_ints[i : i + 2]) for i in range(0, len(arg_ints), 2)),
            )

        if not hasattr(self, "game"):
            print("Game not in progress.")
            return

        try:
            moves: Moves = parse_arg(arg)
        except ValueError as e:
            print(f"Problems with {e}")
            return

        try:
            self.game.play(moves)
        except BoardError:
            print("Illegal move.")
            return

        self._send_update(action="move", move=moves)

    def do_resign(self, arg: str) -> None:
        """Resigns from the match"""
        try:
            if self.game is not None and arg != "":
                if arg.lower() == "single":
                    self.game.resign(Resign.SINGLE_GAME)
                    self._send_update(
                        action="resign", resignation=int(Resign.SINGLE_GAME)
                    )
                elif arg.lower() == "gammon":
                    self.game.resign(Resign.GAMMON)
                    self._send_update(action="resign", resignation=int(Resign.GAMMON))
                elif arg.lower() == "backgammon":
                    self.game.resign(Resign.BACKGAMMON)
                    self._send_update(
                        action="resign", resignation=int(Resign.BACKGAMMON)
                    )
            else:
                self.do_hint(arg="resign")
        except Exception as exc:
            print(exc)

    # Peripheral commands

    def do_print(self, arg: str):
        """Prints the board to stdout"""
        try:
            if self.game is not None:
                print(f"\n{self.game}\n")
            else:
                self.do_hint(arg="print")
        except Exception as exc:
            print(exc)

    def do_hint(self, arg: str):
        """Prints the board to stdout"""
        try:
            if self.game is not None:
                if self._your_turn():
                    if (
                        self.game.match.game_state == GameState.RESIGNED
                        and self._your_turn()
                    ):
                        print(
                            f"Your opponent has offered to resign a {self.game.match.resign.phrase}, accept, or reject?"
                        )
                        return

                    if self.game.match.game_state == GameState.ROLLED:
                        plays = self.game.generate_plays()

                        if len(plays) == 0:
                            print("No legal moves. Resign or end turn.")
                            return

                        for play in plays:
                            # print(plays)
                            human_readable_index = f"{plays.index(play) + 1}."
                            human_readable_play = ""
                            for sub_play in play:
                                if not isinstance(sub_play, tables.position.Position):
                                    for move in sub_play:
                                        source = (
                                            (move.source + 1)
                                            if isinstance(move.source, int)
                                            else "bar"
                                        )
                                        destination = (
                                            (move.destination + 1)
                                            if isinstance(move.destination, int)
                                            else "off"
                                        )
                                        human_readable_play += (
                                            f"{source}/{destination} "
                                        )
                            print(f"    {human_readable_index} {human_readable_play}")
                        return

                    if self.game.match.game_state == GameState.DOUBLED:
                        print(
                            f"Cube offered at {self.game.match.cube_value}, take, drop or redouble?"
                        )
                        return

                    if self.game.match.game_state == GameState.ON_ROLL:
                        print("Roll, double or resign?")
                        return

                    if self.game.match.game_state == GameState.TAKE:
                        print("Double accepted, roll or resign?")
                        return
                else:
                    print("It's not your turn, but you can still send a message.")
                    return
            else:
                print("There is no game started. Type new to start a game.")
        except Exception as exc:
            print(exc)

    def do_message(self, arg: str) -> None:
        """Sends a message to your opponent"""
        try:
            if self.match is not None:
                messages = self.match.get("messages", [])
                if arg != "":
                    message = (
                        datetime.utcnow().isoformat(),
                        self.game.player.player_type,
                        arg,
                    )
                    if self.is_local:
                        messages.append(message)
                        self._update_json_file()
                    elif self._websocket is not None:
                        params = {
                            "message": message,
                            "matchRef": self.match_ref,
                            "player": self.opponent.__dict__(),
                        }
                        request = loads(MessageRequest(**params).json())
                        result = self._send("message", request)
                        logger.debug(result)
                elif len(messages) > 0:
                    for message in messages:
                        print(
                            PlayerType(message[1]).phrase,
                            f"({message[0]}):",
                            message[2],
                        )
                elif len(messages) == 0:
                    print(
                        "No messages in the log. Why not wish your opponent good luck?"
                    )
            else:
                self.do_hint(arg="message")
        except Exception as exc:
            print(exc)

    def do_quit(self, arg: str) -> bool:
        """Exits the program. This also resigns any matches."""
        try:
            continue_quit = input(
                "This will resign you from any matches, do you want to continue? [y/N]: "
            )
            if str(continue_quit).lower() != "y":
                return False
            elif self._websocket is not None:
                self.do_resign("confirmed")
                self._websocket.close()
            return True
        except Exception as exc:
            print(exc)

    def do_pipcount(self, arg: str) -> None:
        """Returns the the total number of points that
        you and your opponent checkers must move
        to bring them home and bear them off."""
        try:
            if self.game is not None:
                if self.game.player.player_type == Player.ZERO:
                    position = self.game.position
                else:
                    position = self.game.position.swap_players()
                player_count, opponent_count = position.pip_count()
                print(f"You: {player_count}, Opponent: {opponent_count}")
            else:
                self.do_hint(arg="pipcount")
        except Exception as exc:
            print(exc)

    def do_playerinfo(self, arg: str) -> None:
        """Displays information about the player"""
        try:
            if self.user_attributes:
                print(dumps(self.user_attributes, indent=4))
            else:
                self.do_hint(arg="player_info")
        except Exception as exc:
            print(exc)

    # Development commands

    # def do_jwt(self, arg: str) -> None:
    #     """Prints JWT information"""
    #     print("\nAccess Token: ", self.jwt_access_token)
    #     print("\nID Token: ", self.jwt_id_token)
    #     print("\nRefresh Token: ", self.jwt_refresh_token)
    #     print("\nCredentials ", self.credentials)

    def do_debug(self, arg: str) -> None:
        """Prints debug information to stdout"""
        try:
            print(
                "Player0",
                ("*" if int(self.game.player) == int(PlayerType.ZERO) else ""),
                sep="",
            )
            print(f"  id: {self.game.player0.playerId}")
            print(f"  username: {self.game.player0.nickname}")
            print(f"  connection_id: {self.game.player0.connectionId}")
            print(f"  rank: {self.game.player0.rank}")
            print(f"  rating: {self.game.player0.rating}")
            print(f"  wins: {self.game.player0.wins}")
            print(f"  losses: {self.game.player0.losses}")
            print(f"  money: {self.game.player0.money}")
            print("  pip_count: ")
            print(
                "Player1",
                ("*" if int(self.game.player) == int(PlayerType.ONE) else ""),
                sep="",
            )
            print(f"  id: {self.game.player1.playerId}")
            print(f"  username: {self.game.player1.nickname}")
            print(f"  connection_id: {self.game.player1.connectionId}")
            print(f"  rank: {self.game.player1.rank}")
            print(f"  rating: {self.game.player1.rating}")
            print(f"  wins: {self.game.player1.wins}")
            print(f"  losses: {self.game.player1.losses}")
            print(f"  money: {self.game.player1.money}")
            print("  pip_count: ")
            print("Match")
            print(f"  ref: {self.match_ref}") if self.match_ref != "" else None
            print(f"  crawford: {self.game.match.crawford}")
            print(f"  cube_holder: {self.game.match.cube_holder}")
            print(f"  cube_value: {self.game.match.cube_value}")
            print(f"  dice: {self.game.match.dice}")
            print(f"  double: {self.game.match.double}")
            (
                print(
                    f"  game_state: {self.game.match.game_state} ({self.game.match.game_state.description})"
                )
                if self.game is not None
                else None
            )
            print(f"  length: {self.game.match.length}")
            print(f"  player: {self.game.match.player}")
            print(f"  player_0_score: {self.game.match.player_0_score}")
            print(f"  player_1_score: {self.game.match.player_1_score}")
            print(f"  resign: {self.game.match.resign}")
            print(f"  turn: {self.game.match.turn}")
        except Exception as exc:
            print(exc)

    def do_load(self, arg: str) -> None:
        self._load_match()
        self.is_local = True
        self.do_print(arg="")

    def do_close(self, arg: str) -> None:
        """Closes the websocket"""
        try:
            if self._websocket is not None:
                print("closing websocket")
                self._websocket.close()
            else:
                self.do_hint(arg="close")
        except Exception as exc:
            print(exc)

    def do_end_turn(self, arg: str) -> None:
        """Ends the turn"""
        try:
            try:
                plays = self.game.generate_plays()
                if len(plays) == 0:
                    self.game.end_turn()
                    self._send_update(action="move", move=None)
                    return
                else:
                    self.do_hint(arg="end_turn")
            except BoardError:
                print("Illegal move.")
                return

        except Exception as exc:
            print(exc)

    # PRIVATE FUNCTIONS
    def _send_update(self, action: str, resignation=None, move=None) -> None:
        """Create an update payload and starts a thread"""
        match_put_request = {
            "matchRef": self.match_ref,
            "resignation": resignation,
            "moves": move,
            "action": action,
        }

        match_put_request = loads(
            MatchPutRequest(**match_put_request).json(exclude_none=True)
        )
        args = (action, match_put_request)

        threading.Thread(target=self._send, name="Send", args=args).start()

    def _send(self, action: str, params: dict) -> None:
        """Sends a payload to the websocket"""
        payload = {
            "action": action,
            **params,
        }
        print(dumps(payload, indent=4))
        # TODO: Remove after development is finished.
        if self.is_local:
            self._update_json_file()
            self.do_print(arg="")
        else:
            self._websocket.send(dumps(payload))
        return

    def _receive(self) -> str:
        """Receives messages from the websocket and processes them."""
        try:
            while self._websocket:
                result = self._websocket.recv()
                print(result)
                if result:
                    # Load the response string
                    self._load_match(result)

                    # Print update stdout
                    if hasattr(self, "game") and self.game is not None:
                        print(f"\n\n{self.game}\n\n{self.prompt}", end="")
        except Exception as exc:
            print(exc)

    def _create_websocket(self) -> None:
        """Creates a websocket object"""
        self._websocket = websocket.create_connection(
            self.websocket_url,
            header=self._headers(),
        )

    def _headers(self) -> dict:
        """Returns a dictionary of headers for the websocket request"""
        auth_headers = self._signed_request_headers()
        # claims_headers = self.claims
        headers = {
            **auth_headers,
            "X-Player-Id": self.player_id,
        }
        return headers

    def _signed_request_headers(self) -> dict:
        """Signs the websocket url and returns the headers"""
        request = AWSRequest(method="GET", url=self.websocket_url)
        SigV4Auth(self.credentials, self.service, self.region).add_auth(request)
        return dict(request.headers.items())

    def _get_credentials(self) -> Union[dict, Credentials]:
        """Gets credentials from a cognito user and returns a botocore Credentials object"""
        try:
            if self.credentials is not None:
                return self.credentials
            else:
                response = self.identity_client.get_credentials_for_identity(
                    IdentityId=self._get_id(),
                    Logins={self.login_path: self.jwt_id_token},
                )
                return Credentials(
                    access_key=response["Credentials"]["AccessKeyId"],
                    secret_key=response["Credentials"]["SecretKey"],
                    token=response["Credentials"]["SessionToken"],
                )
        except Exception as exc:
            print(exc)

    def _get_id(self) -> str:
        """Gets the cognito identity ID of a cognito user"""
        try:
            if self.identity_id is not None:
                return self.identity_id
            else:
                response = self.identity_client.get_id(
                    AccountId=self.account_id,
                    IdentityPoolId=self.identity_pool_id,
                    Logins={self.login_path: self.jwt_id_token},
                )
                return response["IdentityId"]
        except Exception as exc:
            print(exc)

    def _get_unverified_claims(self) -> dict:
        """Decode the user data from the access token"""
        return jwt.get_unverified_claims(self.jwt_access_token)

    def _get_user(self) -> dict:
        """Gets the user attributes and metadata for a user."""
        try:
            if self.jwt_access_token is not None:
                response = self.idp_client.get_user(
                    AccessToken=self.jwt_access_token,
                )
                # The "Username" is not really a username but a user id.
                self.player_id = response["Username"]
                pattern = "^custom:"
                for attribute in response["UserAttributes"]:
                    if re.match(pattern, attribute["Name"]):
                        custom_attribute_name = attribute["Name"].split(":")[-1]
                        self.user_attributes[custom_attribute_name] = attribute["Value"]
                    else:
                        self.user_attributes[attribute["Name"]] = attribute["Value"]
                return response
        except Exception as exc:
            print(exc)

    def _set_response_variables(self, response: str) -> None:
        """

        Args:
            response:

        Returns:

        """
        try:
            logger.debug("Response: %s", response)

            self.match = loads(response)

            self.match_ref = self.match["matchRef"]
            position_id, match_id = self.match["gameId"].split(":")
            bet = self.match["bet"]

            self.game: Board = str_to_class("tables.variants.backgammon", "Backgammon")(
                position_id=position_id, match_id=match_id, bet=bet
            )

            self.game.player0 = Player(PlayerType.ZERO, **self.match["player0"])
            self.game.player1 = Player(PlayerType.ONE, **self.match["player1"])

            if self.game.player0.playerId == self.player_id:
                self.game.player = self.game.player0
                self.opponent = self.game.player1

            elif self.game.player1.playerId == self.player_id:
                self.game.player = self.game.player1
                self.opponent = self.game.player0

            # if self.game.match.game_state == GameState.GAME_OVER:
            #     self.game = None
        except Exception as e:
            traceback.print_exc()
            print(e)

    def _your_turn(self) -> bool:
        """

        Returns:

        """
        return int(self.game.match.player) == int(self.game.player)

    def _update_json_file(self) -> dict:
        """Update the local json file for development"""
        match = {
            **self.match,
            **loads(self.game.to_json()),
        }
        with open(file_path, "w") as json_file:
            json_file.write(dumps(match, indent=4, sort_keys=True))
        return match

    def _load_match(self, response: str = None) -> None:
        """Loads match into variables either from the websocket response or the filesystem"""
        if response is not None:
            self._set_response_variables(response)
        else:
            match_json_file = loads(open(file_path).read())
            self._set_response_variables(match_json_file)
