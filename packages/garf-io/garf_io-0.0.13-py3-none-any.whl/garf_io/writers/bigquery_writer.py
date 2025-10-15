# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Writes GarfReport to BigQuery."""

from __future__ import annotations

import os

try:
  from google.cloud import bigquery
except ImportError as e:
  raise ImportError(
    'Please install garf-io with BigQuery support - `pip install garf-io[bq]`'
  ) from e

import datetime
import logging
from collections.abc import Sequence

import numpy as np
import pandas as pd
import proto  # type: ignore
from garf_core import parsers
from garf_core import report as garf_report
from google.cloud import exceptions as google_cloud_exceptions

from garf_io import exceptions, formatter
from garf_io.writers import abs_writer


class BigQueryWriterError(exceptions.GarfIoError):
  """BigQueryWriter specific errors."""


class BigQueryWriter(abs_writer.AbsWriter):
  """Writes Garf Report to BigQuery.

  Attributes:
    project: Id of Google Cloud Project.
    dataset: BigQuery dataset to write data to.
    location: Location of a newly created dataset.
    write_disposition: Option for overwriting data.
  """

  def __init__(
    self,
    project: str | None = os.getenv('GOOGLE_CLOUD_PROJECT'),
    dataset: str = 'garf',
    location: str = 'US',
    write_disposition: bigquery.WriteDisposition | str = (
      bigquery.WriteDisposition.WRITE_TRUNCATE
    ),
    **kwargs,
  ):
    """Initializes BigQueryWriter.

    Args:
      project: Id of Google Cloud Project.
      dataset: BigQuery dataset to write data to.
      location: Location of a newly created dataset.
      write_disposition: Option for overwriting data.
      kwargs: Optional keywords arguments.
    """
    super().__init__(**kwargs)
    if not project:
      raise BigQueryWriterError(
        'project is required. Either provide it as project parameter '
        'or GOOGLE_CLOUD_PROJECT env variable.'
      )
    self.project = project
    self.dataset_id = f'{project}.{dataset}'
    self.location = location
    if isinstance(write_disposition, str):
      write_disposition = getattr(
        bigquery.WriteDisposition, write_disposition.upper()
      )
    self.write_disposition = write_disposition

  def __str__(self) -> str:
    return f'[BigQuery] - {self.dataset_id} at {self.location} location.'

  @property
  def client(self) -> bigquery.Client:
    """Instantiated BigQuery client."""
    return bigquery.Client(self.project)

  def create_or_get_dataset(self) -> bigquery.Dataset:
    """Gets existing dataset or create a new one."""
    try:
      bq_dataset = self.client.get_dataset(self.dataset_id)
    except google_cloud_exceptions.NotFound:
      bq_dataset = bigquery.Dataset(self.dataset_id)
      bq_dataset.location = self.location
      bq_dataset = self.client.create_dataset(bq_dataset, timeout=30)
    return bq_dataset

  def write(self, report: garf_report.GarfReport, destination: str) -> str:
    """Writes Garf report to a BigQuery table.

    Args:
      report: Garf report.
      destination: Name of the table report should be written to.

    Returns:
      Name of the table in `dataset.table` format.
    """
    report = self.format_for_write(report)
    schema = _define_schema(report)
    destination = formatter.format_extension(destination)
    _ = self.create_or_get_dataset()
    table = self._create_or_get_table(
      f'{self.dataset_id}.{destination}', schema
    )
    job_config = bigquery.LoadJobConfig(
      write_disposition=self.write_disposition,
      schema=schema,
      source_format='CSV',
      max_bad_records=len(report),
    )

    if not report:
      df = pd.DataFrame(
        data=report.results_placeholder, columns=report.column_names
      ).head(0)
    else:
      df = report.to_pandas()
    df = df.replace({np.nan: None})
    logging.debug('Writing %d rows of data to %s', len(df), destination)
    job = self.client.load_table_from_dataframe(
      dataframe=df, destination=table, job_config=job_config
    )
    try:
      job.result()
      logging.debug('Writing to %s is completed', destination)
    except google_cloud_exceptions.BadRequest as e:
      raise ValueError(f'Unable to save data to BigQuery! {str(e)}') from e
    return f'[BigQuery] - at {self.dataset_id}.{destination}'

  def _create_or_get_table(
    self, table_name: str, schema: Sequence[bigquery.SchemaField]
  ) -> bigquery.Table:
    """Gets existing table or create a new one.

    Args:
      table_name: Name of the table in BigQuery.
      schema: Schema of the table if one should be created.

    Returns:
      BigQuery table object.
    """
    try:
      table = self.client.get_table(table_name)
    except google_cloud_exceptions.NotFound:
      table_ref = bigquery.Table(table_name, schema=schema)
      table = self.client.create_table(table_ref)
      table = self.client.get_table(table_name)
    return table


def _define_schema(
  report: garf_report.GarfReport,
) -> list[bigquery.SchemaField]:
  """Infers schema from GarfReport.

  Args:
    report: GarfReport to infer schema from.

  Returns:
    Schema fields for a given report.

  """
  result_types = _get_result_types(report)
  return _get_bq_schema(result_types)


def _get_result_types(
  report: garf_report.GarfReport,
) -> dict[str, dict[str, parsers.ApiRowElement]]:
  """Maps each column of report to BigQuery field type and repeated status.

  Fields types are inferred based on report results or results placeholder.

  Args:
    report: GarfReport to infer field types from.

  Returns:
    Mapping between each column of report and its field type.
  """
  result_types: dict[str, dict[str, parsers.ApiRowElement]] = {}
  column_names = report.column_names
  for row in report.results or report.results_placeholder:
    if set(column_names) == set(result_types.keys()):
      break
    for i, field in enumerate(row):
      if field is None or column_names[i] in result_types:
        continue
      field_type = type(field)
      if field_type in [
        list,
        proto.marshal.collections.repeated.RepeatedComposite,
        proto.marshal.collections.repeated.Repeated,
      ]:
        repeated = True
        field_type = str if len(field) == 0 else type(field[0])
      else:
        field_type = type(field)
        repeated = False
      result_types[column_names[i]] = {
        'field_type': field_type,
        'repeated': repeated,
      }
  return result_types


def _get_bq_schema(
  types: dict[str, dict[str, parsers.ApiRowElement]],
) -> list[bigquery.SchemaField]:
  """Converts report fields types to BigQuery schema fields.

  Args:
    types: Mapping between column names and its field type.

  Returns:
     BigQuery schema fields corresponding to GarfReport.
  """
  type_mapping = {
    list: 'REPEATED',
    str: 'STRING',
    datetime.datetime: 'DATETIME',
    datetime.date: 'DATE',
    int: 'INT64',
    float: 'FLOAT64',
    bool: 'BOOL',
    proto.marshal.collections.repeated.RepeatedComposite: 'REPEATED',
    proto.marshal.collections.repeated.Repeated: 'REPEATED',
  }

  schema: list[bigquery.SchemaField] = []
  for key, value in types.items():
    field_type = type_mapping.get(value.get('field_type'))
    schema.append(
      bigquery.SchemaField(
        name=key,
        field_type=field_type if field_type else 'STRING',
        mode='REPEATED' if value.get('repeated') else 'NULLABLE',
      )
    )
  return schema
