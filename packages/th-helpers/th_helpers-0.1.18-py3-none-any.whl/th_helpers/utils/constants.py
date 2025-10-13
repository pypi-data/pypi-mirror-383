class TIME:
    MINUTE = 60
    HOUR = MINUTE * 60
    HALF_DAY = HOUR * 12
    DAY = HOUR * 24


class DASH:
    '''Constants used for referencing different component
    attributes - primarly for callbacks.
    This list includes attributes for dash.html, dash.dcc,
    and dash-bootstrap-components.
    '''
    ACTIVE = 'active'
    BASE64_IMAGE_STR = 'data:image/png;base64,{}'
    BLANK = '_blank'
    CHILDREN = 'children'
    CLASSNAME = 'className'
    CLASS_NAME = 'class_name'
    CLIENTSIDE = 'clientside'  # script namespace
    COLOR = 'color'
    DATA = 'data'
    DISABLED = 'disabled'
    END_DATE = 'end_date'
    HASH = 'hash'
    HEADER = 'header'
    HREF = 'href'
    ICON = 'icon'
    ID = 'id'
    INDEX = 'index'
    INITIAL_DUPLICATE = 'initial_duplicate'
    INVALID = 'invalid'
    IS_OPEN = 'is_open'
    LABEL = 'label'
    LAST = 'last'
    MAXLENGTH = 'maxlength'
    N_CLICKS = 'n_clicks'
    NUMBER = 'number'
    OPTIONS = 'options'
    ORDER = 'order'
    PAGES_LOCATION = '_pages_location'
    PATHNAME = 'pathname'
    SEARCH='search'
    SIZE = 'size'
    SRC = 'src'
    START_DATE = 'start_date'
    SUBMIT_N_CLICKS = 'submit_n_clicks'
    SUBTYPE = 'subtype'
    TYPE = 'type'
    VALUE = 'value'

    class AIO:
        AIO_ID = 'aio_id'
        COMPONENT = 'component'
        SUBCOMPONENT = 'subcomponent'


class BOOTSTRAP:
    '''Constants specific to Bootstrap
    These are mostly used for coloring or positioning.
    '''
    class ALIGNMENT:
        BOTTOM_END = 'bottom-end'
        CENTER = 'center'
        END = 'end'

    class COLOR:
        DANGER = 'danger'
        DARK = 'dark'
        INFO = 'info'
        LIGHT = 'light'
        PRIMARY = 'primary'
        SECONDARY = 'secondary'
        SUCCESS = 'success'
        TRANSPARENT = 'transparent'
        WARNING = 'warning'


class STYLE:
    '''Constants used when defining inline styles
    '''
    BACKGROUND = 'background'
    HEIGHT = 'height'
    MAXHEIGHT = 'maxHeight'
    MAXWIDTH = 'maxWidth'
    WIDTH = 'width'
