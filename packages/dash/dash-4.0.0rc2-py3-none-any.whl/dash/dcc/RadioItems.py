# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class RadioItems(Component):
    """A RadioItems component.
    RadioItems is a component that encapsulates several radio item inputs.
    The values and labels of the RadioItems is specified in the `options`
    property and the seleced item is specified with the `value` property.
    Each radio item is rendered as an input with a surrounding label.

    Keyword arguments:

    - options (boolean | number | string | dict | list; optional):
        An array of options.

    - value (string | number | boolean; optional):
        The currently selected value.

    - inline (boolean; default False):
        Indicates whether the options labels should be displayed inline
        (True=horizontal) or in a block (False=vertical).

    - inputStyle (boolean | number | string | dict | list; optional):
        The style of the <input> checkbox element.

    - inputClassName (string; default ''):
        The class of the <input> checkbox element.

    - labelStyle (boolean | number | string | dict | list; optional):
        The style of the <label> that wraps the checkbox input  and the
        option's label.

    - labelClassName (string; default ''):
        The class of the <label> that wraps the checkbox input  and the
        option's label.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - className (string; optional):
        Additional CSS class for the root DOM node.

    - persistence (string | number | boolean; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (boolean | number | string | dict | list; default [PersistedProps.value]):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: None, 'local', 'session', 'memory'; default PersistenceTypes.local):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "RadioItems"

    def __init__(
        self,
        options: typing.Optional[typing.Any] = None,
        value: typing.Optional[typing.Union[str, NumberType, bool]] = None,
        inline: typing.Optional[typing.Union[bool]] = None,
        style: typing.Optional[typing.Any] = None,
        inputStyle: typing.Optional[typing.Any] = None,
        inputClassName: typing.Optional[typing.Union[str]] = None,
        labelStyle: typing.Optional[typing.Any] = None,
        labelClassName: typing.Optional[typing.Union[str]] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        className: typing.Optional[typing.Union[str]] = None,
        persistence: typing.Optional[typing.Union[str, NumberType, bool]] = None,
        persisted_props: typing.Optional[typing.Any] = None,
        persistence_type: typing.Optional[
            Literal[None, "local", "session", "memory"]
        ] = None,
        **kwargs
    ):
        self._prop_names = [
            "options",
            "value",
            "inline",
            "style",
            "inputStyle",
            "inputClassName",
            "labelStyle",
            "labelClassName",
            "id",
            "className",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "options",
            "value",
            "inline",
            "style",
            "inputStyle",
            "inputClassName",
            "labelStyle",
            "labelClassName",
            "id",
            "className",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(RadioItems, self).__init__(**args)


setattr(RadioItems, "__init__", _explicitize_args(RadioItems.__init__))
