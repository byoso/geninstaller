#! /usr/bin/env python3

import sys
from typing import Any

WIDTH=80

class RouterError(Exception):
    def __init__(self, message: str="Router Error", status: int | None=None, *args, **kwargs):
        self.status = status
        self.message = message
        super().__init__({'status': self.status, 'message': self.message})


class Subrouter:
    def __init__(self, prefix, router, description):
        self.prefix = prefix
        self.router = router
        self.description = description


class Router:
    def __init__(
            self,
            routes: list = list(),
            name: str="Silly Router",
            separator: str=" ",
            query_separator="?",
            queries_separator="+",
            width=WIDTH):
        self.name = name
        self.separator = separator
        self.query_separator = query_separator
        self.queries_separator = queries_separator
        self._routes = {}
        self._subroutes = {}
        self._help = []
        self.welcoming = f"\n##### '{self.name}' help "
        self.width = width
        self.logging = True
        self.__datas = {
            "building_paths": [],
            "logs": []
        }

        if routes is not None:
            self.add_routes(routes)

    def add_routes(self, routes: list) -> None:
        try:
            assert isinstance(routes, list) or isinstance(routes, tuple)
        except AssertionError:
            raise RouterError("Router building: Routes must be a list or a tuple")
        for route in routes:
            self.add_route(route)

    def add_route(self, incoming_route: str | Subrouter | list) -> None:
        # route is a string (comment)
        if isinstance(incoming_route, str):
            self._help.append("# " + incoming_route)
            return
        # route is a subrouter
        if isinstance(incoming_route, Subrouter):
            self._help.append(f"@ {incoming_route.prefix:<50} -> {incoming_route.description}")
            self._subroutes[incoming_route.prefix] = incoming_route.router
            return

        # route is a list or a tuple:
        try:
            assert isinstance(incoming_route, list) or isinstance(incoming_route, tuple)
        except AssertionError:
            raise RouterError("Route building: A route must be a list, a tuple, or a Subrouter")

        if not 2 <= len(incoming_route) <= 3:
            raise RouterError(
                "Route building: A route must have 2 or 3 elements <route, callable, description (Optional)>")
        if not isinstance(incoming_route[0], (str, list, tuple)):
            raise RouterError("Route building: The 1st element of a route must be a string, list, or tuple",)
        if len(incoming_route) == 3:
            if not isinstance(incoming_route[2], str):
                raise RouterError(
                    "Route building: The 3rd element of a route must be a string as a description for the help")
            self._help.append(f"- {str(incoming_route[0]):<50} -> {str(incoming_route[2])}")
        else:
            incoming_route.append("")
        if not callable(incoming_route[1]):
            raise RouterError("Route building: The 2nd element of a route must be callable")
        self._build_route(incoming_route)

    @property
    def logs(self):
        logs = self.__datas["logs"]
        self.__datas["logs"] = []
        return logs

    def _build_route(self, incoming_route: tuple | list) -> None:
        # if multi route possible
        if isinstance(incoming_route[0], (tuple, list)):
            for route in incoming_route[0]:
                self._build_route((route, incoming_route[1], incoming_route[2]))
            return
        if isinstance(incoming_route[0], str):
            path = incoming_route[0].split(self.separator)
        else:
            raise RouterError("Route building: A route must be a string, list of str, or tuple of str")

        # dictionary by legnth of path
        if not len(path) in self._routes:
            self._routes[len(path)] = [[incoming_route[1], path, incoming_route[2]]]
        else:
            self._routes[len(path)].append([incoming_route[1], path, incoming_route[2]])
        # log if path is overwritten
        if path in self.__datas["building_paths"]:
            self._routes[len(path)] = list(filter(lambda x: x[1] != path, self._routes[len(path)]))
            self._routes[len(path)].append([incoming_route[1], path, incoming_route[2]])
            if self.logging:
                self.__datas["logs"].append(f"WARNING: Path {path} has been overwritten")
        else:
            self.__datas["building_paths"].append(path)

    @property
    def help(self, **kwargs) -> str | Any:
        help = self.welcoming + "#" * (self.width - len(self.welcoming)) + "\n"
        for line in self._help:
            help += line + "\n"
        help += "\n" + "#" * self.width
        return help

    def display_help(self, **kwargs) -> None:
        print(self.help)


    def query(self, query: str | list =sys.argv[1:], method='GET', context={}, query_params=None):
        if isinstance(query, list):
            try:
                query = self.separator.join(query)
            except TypeError:
                raise RouterError("Bad query: Query must be a string or a list of strings")
        if query.count(self.query_separator) > 1:
            raise RouterError(f"Bad query: Query must have only one '{self.query_separator}' separator")
        path = query.split(self.query_separator)[0].strip().split(self.separator)
        params = query.split(self.query_separator)[1].strip().split(self.queries_separator) if self.query_separator in query else None

        if len(path) > 0 and path[0] in self._subroutes:
            return self._subroutes[path[0]].query(path[1:], query_params=params, context=context)
        if query_params is None:
            query_params = {}
            if params:
                for param in params:
                    query_params[param.strip().split("=")[0]] = param.strip().split("=")[1]
        if self._routes.get(len(path)) is None:
            raise RouterError(f"Route not found for path: {path}", 404)
        route = self._get_route(path, self._routes.get(len(path)))
        kwargs = self._get_kwargs(route, path)
        if query_params:
            kwargs["query_params"] = query_params
        if context:
            kwargs["context"] = context
        if kwargs:
            return route[0](**kwargs)
        return route[0]()

    def _get_kwargs(self, route, query):
        kwargs = {}
        index = 0
        for key in route[1]:
            if key.startswith("<") and key.endswith(">"):
                value = query[index]
                if ":" in key:
                    typing = key[1:-1].split(":")[1]
                    key = key[1:-1].split(":")[0]
                    try:
                        if typing == "int":
                            value = int(value)
                        elif typing == "float":
                            value = float(value)
                        elif typing == "bool":
                            value = bool(int(value))
                    except ValueError:
                        raise RouterError(f"Bad query: Value '{value}' for '{key}' is not the expected type '{typing}'", status=400)
                    kwargs[key] = value
                else:
                    key = key.strip("<").strip(">").strip()
                    kwargs[key] = value
            index += 1
        return kwargs

    def _get_route(self, path, available_routes, index=0):
        if index >= len(path):
            if len(available_routes) == 0:
                raise RouterError(f"Route not found for path: {path}", 404)
            elif len(available_routes) > 1:
                raise RouterError(f"Uncaught ambiguity: {[route[1] for route in available_routes]}", 500)
            else:
                return available_routes[0]
        sure_list = []
        unsure_list = []
        for route in available_routes:
            if route[1][index] == path[index]:
                sure_list.append(route)
            elif route[1][index].startswith("<") and route[1][index].endswith(">"):
                unsure_list.append(route)
        if len(sure_list) > 0:
            return self._get_route(path, sure_list, index+1)
        elif len(unsure_list) > 0:
            return self._get_route(path, unsure_list, index+1)
        else:
            raise RouterError(f"Route not found for path: {path}", 404)
