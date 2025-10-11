## import standard libraries
from typing import Dict, List, Optional, Self
## import local files
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.schemas.tables.FeatureMapSchema import FeatureMapSchema
from ogd.common.utils import typing

## @class TableSchema
class FeatureTableSchema(TableSchema):
    """Dumb struct to hold info about the structure of data for a particular game, from a particular source.
        In particular, it contains an ordered list of columns in the data source table,
        and a mapping of those columns to the corresponding elements of a formal OGD structure.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name,
                 column_map:Optional[FeatureMapSchema],
                 columns:Optional[List[ColumnSchema]],
                 other_elements:Optional[typing.Map]=None
        ):
        """Constructor for the TableSchema class.
        Given a database connection and a game data request,
        this retrieves a bit of information from the database to fill in the
        class variables.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "column_map": {
                "session_id"           : "session_id",
                "app_id"               : null,
                "timestamp"            : ["client_time", "client_time_ms"],
                ...
            },

            "columns": [
                {
                    "name": "session_id",
                    "readable": "Session ID",
                    "description": "ID for the play session",
                    "type": "str"
                },
                {
                    "name": "client_time",
                    ...
                },
        },
        ```

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to "./schemas/table_schemas/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        unparsed_elements : typing.Map = other_elements or {}

        self._column_map : FeatureMapSchema = column_map if column_map is not None else self._parseColumnMap(unparsed_elements=unparsed_elements, schema_name=name)
        super().__init__(name=name, columns=columns, other_elements=unparsed_elements)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def ColumnMap(self) -> FeatureMapSchema:
        """Mapping from Event element names to the indices of the database columns mapped to them.
        There may be a single index, indicating a 1-to-1 mapping of a database column to the element;
        There may be a list of indices, indicating multiple columns will be concatenated to form the element value;
        There may be a further mapping of keys to indices, indicating multiple columns will be joined into a JSON object, with keys mapped to values found at the columns with given indices.

        :return: The dictionary mapping of element names to indices.
        :rtype: Dict[str, Union[int, List[int], Dict[str, int], None]]
        """
        return self._column_map
    @property
    def Map(self) -> FeatureMapSchema:
        """Alias for ColumnMap property

        Mapping from Event element names to the indices of the database columns mapped to them.
        There may be a single index, indicating a 1-to-1 mapping of a database column to the element;
        There may be a list of indices, indicating multiple columns will be concatenated to form the element value;
        There may be a further mapping of keys to indices, indicating multiple columns will be joined into a JSON object, with keys mapped to values found at the columns with given indices.

        :return: The dictionary mapping of element names to indices.
        :rtype: Dict[str, Union[int, List[int], Dict[str, int], None]]
        """
        return self.ColumnMap

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        _columns_markdown = "\n".join([item.AsMarkdown for item in self.Columns])
        ret_val = "\n\n".join([
            "## Database Columns",
            "The individual columns recorded in the database for this game.",
            _columns_markdown,
            "## Feature Object Elements",
            "The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.",
            self.ColumnMap.AsMarkdown,
            ""]
        )
        return ret_val

    @classmethod
    def Default(cls) -> "FeatureTableSchema":
        return FeatureTableSchema(
            name="DefaultFeatureTableSchema",
            column_map=FeatureMapSchema.Default(),
            columns=cls._DEFAULT_COLUMNS,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:typing.Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "FeatureTableSchema":
        """Function to generate a TableSchema from a dictionary.

        The structure is assumed to be as follows:
        ```python
        {
            "table_type" : <either EVENT or FEATURE>,
            "columns" : [<list of column schemas>],
            "column_map" : {<mapping of column names to indices>}
        }
        ```

        The specific handling of the column map will be determined by the specific TableSchema subclass on which the FromDict feature is called.

        :param name: The name of the returned TableSchema object
        :type name: str
        :param all_elements: A dictionary containing all elements to be parsed into the TableSchema object
        :type all_elements: Dict[str, Any]
        :param logger: An optional logger for outputting errors/warnings, defaults to None
        :type logger: Optional[logging.Logger], optional
        :return: An instance of the TableSchema subclass on which the function is called
        :rtype: TableSchema
        """
        return FeatureTableSchema(name=name, column_map=None, columns=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    @staticmethod
    def _parseColumnMap(unparsed_elements:typing.Map, schema_name:Optional[str]=None) -> FeatureMapSchema:
        ret_val : FeatureMapSchema

        raw_map = TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["column_map"],
            to_type=dict,
            default_value=None,
            remove_target=True,
            schema_name=schema_name
        )
        if raw_map:
            ret_val = FeatureMapSchema.FromDict(name="ColumnMap", unparsed_elements=raw_map)
        else:
            ret_val = FeatureMapSchema.Default()

        return ret_val
