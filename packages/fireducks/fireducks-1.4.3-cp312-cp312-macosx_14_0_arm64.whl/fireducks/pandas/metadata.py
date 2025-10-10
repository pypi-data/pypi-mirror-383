# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

from datetime import datetime
from typing import Any, Union, List
import logging

from pandas.core.indexes.frozen import FrozenList
import numpy as np
import pandas

import fireducks.pandas.utils as utils
from fireducks import ir
from fireducks.fireducks_ext import (
    ColumnMetadata,
    ColumnName,
    IndexMetadata,
    IndexMetadataIndex,
    IndexMetadataIndexRange,
    Metadata,
    Scalar,
)

logger = logging.getLogger(__name__)


class IRMetadataWrapper:
    """
    This class is a wrapper of a metadata defined by IR.

    This class provide convenient methods to use IR metadata.

    In this document, following example is used.

    >>> df
    Month       Jan                 Feb
    Day         Mon       Tue       Mon       Tue
    ABC
    a      0.476154  0.803732  0.520757  0.170070
    b      0.363055  0.919802  0.135537  0.755907
    c      0.939023  0.999877  0.596680  0.628549
    """

    def __init__(self, meta):
        self.meta = meta

    @property
    def column_names(self):
        """
        Column names
        """
        return self.meta.column_names

    @property
    def num_col(self):
        """
        Number of columns
        """
        return len(self.meta.column_names)

    # Map from fireducks IR data type to pandas dtype.
    # Pandas changes data type when null, missing values, exists.
    #
    # Reference:
    #   [1] https://numpy.org/doc/stable/reference/arrays.scalars.html
    #   [2] https://pandas.pydata.org/docs/user_guide/basics.html#dtypes

    class DtypeInfo:
        def __init__(self, dtype, nullable=True, nulltype=None):
            self.dtype = dtype
            self.nullable = nullable
            nulltype = nulltype or np.dtype(np.float64)
            self.nulltype = dtype if nullable else nulltype

    _dtype_info_map = {
        "bool": DtypeInfo(np.dtype(np.bool_), False, np.dtype(np.object_)),
        "int8": DtypeInfo(np.dtype(np.int8), False),
        "int16": DtypeInfo(np.dtype(np.int16), False),
        "int32": DtypeInfo(np.dtype(np.int32), False),
        "int64": DtypeInfo(np.dtype(np.int64), False),
        "uint8": DtypeInfo(np.dtype(np.uint8), False),
        "uint16": DtypeInfo(np.dtype(np.uint16), False),
        "uint32": DtypeInfo(np.dtype(np.uint32), False),
        "uint64": DtypeInfo(np.dtype(np.uint64), False),
        "halffloat": DtypeInfo(np.dtype(np.float16)),
        "float": DtypeInfo(np.dtype(np.float32)),
        "double": DtypeInfo(np.dtype(np.float64)),
        "utf8": DtypeInfo(np.dtype(np.object_)),
        "large_utf8": DtypeInfo(np.dtype(np.object_)),
        "date32": DtypeInfo(np.dtype(np.object_)),
        "list": DtypeInfo(np.dtype(np.object_)),
        "timestamp": DtypeInfo(np.dtype("datetime64[ns]")),
        "duration[s]": DtypeInfo(np.dtype("timedelta64[s]")),
        "duration[ms]": DtypeInfo(np.dtype("timedelta64[ms]")),
        "duration[us]": DtypeInfo(np.dtype("timedelta64[us]")),
        "duration[ns]": DtypeInfo(np.dtype("timedelta64[ns]")),
        # pandas, and numpy, supports following data types, but since it can
        # not be converted to arrow, those types are never used here.
        #   - float128
        #   - complex64
        #   - complex128
        #   - complex256
        # Category types are "dictionary" in fireducks IR data type as arrow.
        # Because pandas's CategoricalDtype has categories, i.e.  values of
        # dictionary and it can not be created only from metadata, it is not in
        # the map. It is taken care differently inside '_get_dtypes()'.
    }

    def _get_dtypes(self, data):
        """
        Data types of columns
        """

        def get_timestamp_dtype(col):
            unit = "ns" if pandas.__version__ < "2" else col.unit

            if len(col.timezone) == 0:
                return np.dtype(f"datetime64[{unit}]")
            else:
                import pytz

                if col.timezone[0] in ["+", "-"]:
                    from datetime import datetime

                    # Parse "+09:00" as UTC offset format and convert to minutes
                    minutes = (
                        datetime.strptime(col.timezone, "%z")
                        .tzinfo.utcoffset(None)
                        .total_seconds()
                        / 60
                    )
                    tz_obj = pytz.FixedOffset(minutes)
                else:
                    tz_obj = pytz.timezone(col.timezone)

                return pandas.api.types.DatetimeTZDtype(unit, tz=tz_obj)

        def get_dtype(col_idx, unsupported):
            col = self.meta.additional_column_metadata_vector[col_idx]
            if col.dtype == "timestamp":
                dtype_obj = get_timestamp_dtype(col)
                info = IRMetadataWrapper.DtypeInfo(dtype_obj)
            elif col.dtype.startswith("dictionary"):
                from fireducks.pandas.series import Series

                # Currently it returns pandas.CategoricalDtype() with
                # 'category' of type pandas.Index (instead of fireducks.Index)
                # TODO: To avoid such a mixed dtype issue (fireducks methods
                # returning pandas object), Wrap pandas.CategoricalDtype.
                s = data if isinstance(data, Series) else data.iloc[:, col_idx]
                dtype_obj = pandas.CategoricalDtype(
                    Series._create(ir.cat_categories(s._value)).to_pandas(),
                    ordered=col.is_ordered_categorical_column,
                )
                info = IRMetadataWrapper.DtypeInfo(dtype_obj)
            else:
                info = IRMetadataWrapper._dtype_info_map.get(col.dtype)
                if info is None:
                    unsupported += [col.dtype]
                    return None

            return info.dtype if col.null_count == 0 else info.nulltype

        unsupported = []
        dtypes = [
            get_dtype(col_idx, unsupported) for col_idx in range(self.num_col)
        ]
        if len(unsupported) > 0:
            return None, unsupported
        idx = (
            pandas.MultiIndex.from_tuples(self.meta.column_names)
            if self.meta.is_multi_level_column_index
            else self.meta.column_names
        )
        return pandas.Series(dtypes, index=idx), []

    def _get_raw_dtypes(self) -> list[str]:
        """
        Return raw dtypes as list of strings.
        """
        out = []
        acmv = self.meta.additional_column_metadata_vector
        for col in acmv:
            if col.dtype == "halffloat":
                t = "float16"
            elif col.dtype == "float":
                t = "float32"
            elif col.dtype == "double":
                t = "float64"
            else:
                t = col.dtype
            out.append(t)
        return out

    def create_column_index(self):
        """
        Return column index as pandas class.

        >>> Example
        col_names = [('Jan', 'Mon'), ('Jan', 'Tue'), ...]
        idx_names = ['Month', 'Day']
        """
        col_names = self.meta.column_names
        idx_names = self.meta.column_index_names
        if self.meta.is_multi_level_column_index:
            return pandas.MultiIndex.from_tuples(col_names, names=idx_names)
        return pandas.Index(col_names, name=idx_names[0], tupleize_cols=False)

    # row index
    def apply_index_metadata(self, df):
        assert self.meta.additional_index_metadata is not None
        index_metadata = self.meta.additional_index_metadata

        # At least table has one index as pandas assigns RangeIndex
        assert len(index_metadata.indexes) > 0

        indexes = []
        to_be_drop = []
        for index in index_metadata.indexes:
            if index.is_range_index:
                r = index.range
                indexes += [
                    pandas.RangeIndex(r.start, r.stop, r.step, name=index.name)
                ]
            else:
                to_be_drop += [index.pos]
                s = df.iloc[:, index.pos]
                if isinstance(index.name, list):
                    # If index.name is list, it is multiindex.
                    indexes += [pandas.Index(s, name=tuple(index.name))]
                else:
                    # If index.name is None, use rename().
                    indexes += [pandas.Index(s.rename(index.name))]

        df = df.drop(df.columns[to_be_drop], axis=1)

        if (
            not self.meta.is_multilevel_row_index
        ):  # index_metadata.isMultiLevel:
            if len(indexes) > 1:
                raise RuntimeError("multiple indexes with isMultiLevel=False")
            indexes = indexes[0]

        df.index = indexes
        return df

        # `df.set_index` does not work when length of df and indexes are
        # different. This happens when df is empty.
        # return df.set_index(indexes)

    def apply(self, df: pandas.DataFrame):
        """
        Apply this metadata to the given dataframe.
        """
        df = self.apply_index_metadata(df)
        columnAsRange = False
        if len(df.columns) == 0 and not self.meta.is_multi_level_column_index:
            if utils._pd_version_under2:
                # This case we use RangeIndex as pandas. See GT #1363
                columnAsRange = isinstance(df.index, pandas.RangeIndex)
            else:
                """
                df = pandas.DataFrame()
                pandas 2.2
                    df.index        :  RangeIndex(start=0, stop=0, step=1)
                    df.columns      :  RangeIndex(start=0, stop=0, step=1)
                pandas 1.5.3
                    df.index        :  Index([], dtype='object')
                    df.columns      :  Index([], dtype='object')
                """
                columnAsRange = True

        df.columns = (
            pandas.RangeIndex(0, 0, 1)
            if columnAsRange
            else self.create_column_index()
        )

        return df

    def is_column_name(self, name):
        """
        Test if name is a column name.
        """
        return name in self.meta.column_names


def _name_to_column_name(name, is_multi_level):
    """
    Convert index name to ColumnName.

    Parameters:
    name: The index name to convert. Can be a single value, frozenset, tuple,
          or FrozenList.
    is_multi_level (bool): Whether this is for a multi-level index structure.

    Returns:
    ColumnName: A ColumnName object, either SingleFromScalars or MultiFromScalars
               depending on the is_multi_level parameter.
    """
    if is_multi_level:
        # pandas uses FrozenList for pandas.DataFrame.index.name.
        if isinstance(name, (frozenset, tuple, FrozenList)):
            scalars = []
            for top_name in name:
                if isinstance(top_name, (frozenset, tuple, FrozenList)):
                    single_name = [make_scalar(child) for child in top_name]
                else:
                    single_name = make_scalar(top_name)
                scalars.append(single_name)

            return ColumnName.MultiFromScalars(scalars)
        else:
            return ColumnName.MultiFromScalars([make_scalar(name)])
    else:
        if isinstance(name, (frozenset, tuple, FrozenList)):
            single_name = [make_scalar(child) for child in name]
        else:
            single_name = make_scalar(name)
        return ColumnName.SingleFromScalars(single_name)


def _columns_to_columns_metadata(columns):
    """
    Convert columns to ColumnMetadata list.

    Parameters:
    columns: The pandas column index to convert. Can be a pandas.Index or
            pandas.MultiIndex containing column names.

    Returns:
    list[ColumnMetadata]: A list of ColumnMetadata objects, one for each column.
    """
    metadata = []
    is_multi = isinstance(columns, pandas.MultiIndex)
    for name in columns:
        column_name = _name_to_column_name(name, is_multi)
        metadata.append(ColumnMetadata(column_name))
    return metadata


def _index_to_columns_metadata(index):
    """
    Convert index to ColumnMetadata list.

    Parameters:
    index: The pandas index to convert. Can be a pandas.Index or pandas.MultiIndex
           containing index names and values.

    Returns:
    list[ColumnMetadata]: A list of ColumnMetadata objects, one for each index level.
    """
    metadata = []
    is_multi = isinstance(index, pandas.MultiIndex)
    index_num = len(index.levels) if is_multi else 1
    for n in range(index_num):
        nth_index = index.get_level_values(n)
        column_name = _name_to_column_name(nth_index.name, False)
        metadata.append(ColumnMetadata(column_name))

    return metadata


def _add_index_metadata(metadata, index):
    """
    Add IndexMetadata to Metadata.

    Parameters:
    metadata (Metadata): The existing metadata object to which index metadata
                        will be added.
    index: The pandas index to convert to IndexMetadata. Can be a pandas.Index
           or pandas.MultiIndex.

    Returns:
    Metadata: Updated metadata object with additional index metadata included.
    """
    meta_list = []
    is_multi = isinstance(index, pandas.MultiIndex)
    index_num = len(index.levels) if is_multi else 1
    for n in range(index_num):
        nth_index = index.get_level_values(n)
        if isinstance(nth_index, pandas.RangeIndex):
            index_range = IndexMetadataIndexRange(
                nth_index.start, nth_index.stop, nth_index.step
            )
            n = -1
        else:
            index_range = IndexMetadataIndexRange(0, 0, 0)
        name = _name_to_column_name(nth_index.name, False)
        index_meta = IndexMetadataIndex(name, n, index_range)
        meta_list.append(index_meta)

    return metadata.with_additional_index_metadata(IndexMetadata(meta_list))


def _index_name_to_column_name(index):
    """
    Convert Index.name to ColumnName.

    Parameters:
    index: The pandas index whose name(s) will be converted. Can be a pandas.Index
           or pandas.MultiIndex.

    Returns:
    ColumnName: A ColumnName object representing the index name(s).
    """
    is_multi = isinstance(index, pandas.MultiIndex)
    if is_multi:
        return _name_to_column_name(index.names, is_multi)
    else:
        return _name_to_column_name(index.names[0], is_multi)


def create_metadata(df):
    """
    Create IR metadata to pass to from_pandas.

    Parameters:
    df (pandas.DataFrame): The pandas DataFrame for which to create metadata.

    Returns:
    Metadata: A complete Metadata object containing column metadata, index metadata,
             column index names, and additional index metadata for IR processing.
    """
    logger.debug("create_metadata: df.columns.nlevels=%d", df.columns.nlevels)
    logger.debug("create_metadata: df.columns.names=%s", df.columns.names)
    logger.debug(
        "create_metadata: isMultiindex=%s",
        isinstance(df.columns, pandas.MultiIndex),
    )

    columns_meta = _columns_to_columns_metadata(df.columns)
    index_meta = _index_to_columns_metadata(df.index)
    column_index_names = _index_name_to_column_name(df.columns)
    metadata = Metadata(
        columns_meta,
        index_meta,
        column_index_names,
        isinstance(df.index, pandas.MultiIndex),
    )
    metadata = _add_index_metadata(metadata, df.index)
    return metadata


def make_scalar(name):
    """
    Create C++ fireducks::Scalar from python object

    See MainModule.cc to know which type of python object is allowed.
    """

    if isinstance(name, datetime):
        return Scalar.from_datetime(name)
    elif isinstance(name, pandas.Timestamp):
        return Scalar.from_timestamp(name)
    elif isinstance(name, pandas.Timedelta):
        return Scalar.from_timedelta(name)
    elif isinstance(name, bytes):
        return Scalar.from_bytes(name)
    else:
        return Scalar(name)


def cudf_get_metadata_impl(df, is_wrapped):
    """
    Used as implementation of GetMetadata of cudf backend
    Mostly same as create_metadata, but the input is different

    Parameters:
    df: Table Object (DataFrame/Series)

    Returns:
    Metadata
    """
    import cudf
    import cudf.pandas._wrappers.pandas

    def my_isinstance(obj, type, has_cudf):
        if isinstance(obj, getattr(pandas, type)) or (
            has_cudf and isinstance(obj, getattr(cudf, type))
        ):
            return True
        elif is_wrapped and isinstance(
            obj, getattr(cudf.pandas._wrappers.pandas, type)
        ):
            return True
        else:
            return False

    def is_wrapped_instance(obj, type):
        if is_wrapped and isinstance(
            obj, getattr(cudf.pandas._wrappers.pandas, type)
        ):
            return True
        else:
            return False

    def my_make_scalar(name):
        if isinstance(name, datetime):
            return Scalar.from_datetime(name)
        elif my_isinstance(name, "Timestamp", False):
            if is_wrapped_instance(name, "Timestamp"):
                return Scalar.from_timestamp(name._fsproxy_fast_to_slow())
            else:
                return Scalar.from_timestamp(name)
        elif my_isinstance(name, "Timedelta", False):
            if is_wrapped_instance(name, "Timedelta"):
                return Scalar.from_timedelta(name._fsproxy_fast_to_slow())
            else:
                return Scalar.from_timedelta(name)
        else:
            return Scalar(name)

    def is_frozen_list(name):
        return isinstance(name, FrozenList) or (
            is_wrapped
            and isinstance(name, cudf.pandas._wrappers.pandas.FrozenList)
        )

    def my_name_to_column_name(name, is_multi_level):
        # replace make_scalar from _name_to_column_name, change FrozenList check
        if is_multi_level:
            # pandas uses FrozenList for pandas.DataFrame.index.name.
            if isinstance(name, (frozenset, tuple)) or is_frozen_list(name):
                scalars = []
                for top_name in name:
                    if isinstance(top_name, (frozenset, tuple, FrozenList)):
                        single_name = [
                            my_make_scalar(child) for child in top_name
                        ]
                    else:
                        single_name = my_make_scalar(top_name)
                    scalars.append(single_name)
                return ColumnName.MultiFromScalars(scalars)
            else:
                return ColumnName.MultiFromScalars([my_make_scalar(name)])
        else:
            if isinstance(name, (frozenset, tuple)) or is_frozen_list(name):
                single_name = [my_make_scalar(child) for child in name]
            else:
                single_name = my_make_scalar(name)
            return ColumnName.SingleFromScalars(single_name)

    def my_index_name_to_column_name(index):
        # replace _name_to_column_name, change is_multi implementation
        is_multi = my_isinstance(index, "MultiIndex", True)
        if is_multi:
            return my_name_to_column_name(index.names, is_multi)
        else:
            return my_name_to_column_name(index.names[0], is_multi)

    def my_index_to_columns_metadata(index):
        # replace _name_to_column_name, change is_multi implementation
        metadata = []
        is_multi = my_isinstance(index, "MultiIndex", True)
        index_num = len(index.levels) if is_multi else 1
        for n in range(index_num):
            nth_index = index.get_level_values(n)
            column_name = my_name_to_column_name(nth_index.name, False)
            metadata.append(ColumnMetadata(column_name))
        return metadata

    if my_isinstance(df, "Series", True):
        columns_meta = [ColumnMetadata(my_name_to_column_name(df.name, False))]
        index_meta = my_index_to_columns_metadata(df.index)
        column_index_names = ColumnName.none()
        metadata = Metadata(
            columns_meta,
            index_meta,
            column_index_names,
            my_isinstance(df.index, "MultiIndex", True),
        )
        metadata = _add_index_metadata(metadata, df.index)
        return metadata
    elif my_isinstance(df, "DataFrame", True):
        is_multi_level = my_isinstance(df.columns, "MultiIndex", True)
        column_names = [
            my_name_to_column_name(name, is_multi_level) for name in df.columns
        ]
        columns_meta = [ColumnMetadata(name) for name in column_names]
        index_meta = my_index_to_columns_metadata(df.index)
        column_index_names = my_index_name_to_column_name(df.columns)
        metadata = Metadata(
            columns_meta,
            index_meta,
            column_index_names,
            my_isinstance(df.index, "MultiIndex", True),
        )
        metadata = _add_index_metadata(metadata, df.index)
        return metadata
    else:
        return None
