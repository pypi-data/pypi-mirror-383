import time
import pandas as pd
import numpy as np
from typing import List, Optional, Generator, Callable, Any
from rand_engine.main.rand_generator import RandGenerator
from rand_engine.file_handlers.writer_batch import FileBatchWriter
from rand_engine.file_handlers.writer_stream import FileStreamWriter
from rand_engine.utils.stream_handler import StreamHandler
from rand_engine.validators.spec_validator import SpecValidator
from rand_engine.validators.exceptions import SpecValidationError

  
class DataGenerator:
      
  def __init__(self, random_spec, seed: int = None, validate: bool = True):
    """
    Inicializa o gerador de dados.
    
    Args:
        random_spec: Especificação de dados (dict)
        seed: Seed para reprodutibilidade (opcional)
        validate: Se True, valida a spec antes de inicializar (padrão: True)
    
    Raises:
        SpecValidationError: Se a spec for inválida e validate=True
    
    Examples:
        >>> spec = {"age": {"method": Core.gen_ints, "kwargs": {"min": 18, "max": 65}}}
        >>> engine = DataGenerator(spec, seed=42)
        >>> df = engine.mode("pandas").size(1000).get_df()
    """
    if validate:
      SpecValidator.validate_and_raise(random_spec)
    
    np.random.seed(seed)
    self.actual_dataframe: Optional[Callable[[], pd.DataFrame]] = None
    self.data_generator = RandGenerator(random_spec, validate=False)  # Já validado
    self._mode = "pandas"
    self._size = 1000
    self.write = self._writer()
    self.writeStream = self._stream_writer()
    self._transformers: List[Optional[Callable]] = []

 
  def generate_pandas_df(self, size: int) -> pd.DataFrame:
    """
    This method generates a pandas DataFrame based on random data specified in the metadata parameter.
    :param size: int: Number of rows to be generated.
    :param transformer: Optional[Callable]: Function to transform the generated data.
    :return: pd.DataFrame: DataFrame with the generated data.
    """
    def wrapped_lazy_dataframe():
      df_pandas = self.data_generator.generate_first_level(size=size)
      df_pandas = self.data_generator.handle_splitable(df_pandas)
      df_pandas = self.data_generator.apply_embedded_transformers(df_pandas)
      df_pandas = self.data_generator.apply_global_transformers(df_pandas, self._transformers)
      return df_pandas
    self.actual_dataframe = wrapped_lazy_dataframe
  

  def transformers(self, transformers: List[Optional[Callable]]):
    self._transformers = transformers
    return self
  

  def generate_spark_df(self, spark, size: int) -> Any:
    """
    This method generates a Spark DataFrame based on random data specified in the random_spec parameter.
    :param spark: SparkSession: SparkSession object.
    :param size: int: Number of rows to be generated.
    :param transformer: Optional[Callable]: Function to transform the generated data."""
    def wrapped_lazy_dataframe():
      self.generate_pandas_df(size=size)
      df_spark = spark.createDataFrame(self.actual_dataframe())
      return df_spark
    self.actual_dataframe = wrapped_lazy_dataframe

  def mode(self, mode: str):
    assert mode in ["pandas", "spark"], "Mode not recognized. Use 'pandas' or 'spark'."
    self._mode = mode
    return self

  def size(self, size: int):
    self._size = size
    return self

  def get_df(self, spark=None):
    if self._mode == "pandas":
      self.generate_pandas_df(size=self._size)
    elif self._mode == "spark":
      self.generate_spark_df(spark=spark, size=self._size)
    assert self.actual_dataframe is not None, "You need to generate a DataFrame first."
    return self.actual_dataframe()


  def stream_dict(self, min_throughput: int=1, max_throughput: int = 10) -> Generator:
    """
    This method creates a generator of records to be used in a streaming context.
    :param min_throughput: int: Minimum throughput to be generated.
    :param max_throughput: int: Maximum throughput to be generated.
    :return: Generator: Generator of records.
    """
    self.generate_pandas_df(size=self._size)
    assert self.actual_dataframe is not None, "You need to generate a DataFrame first."
    while True:
      df_data_microbatch = self.actual_dataframe()
      df_data_parsed = StreamHandler.convert_dt_to_str(df_data_microbatch)
      list_of_records = df_data_parsed.to_dict('records')
      for record in list_of_records:
        record["timestamp_created"] = round(time.time(), 3)
        yield record
        StreamHandler.sleep_to_contro_throughput(min_throughput, max_throughput)
  

  def _writer(self):
    df_callable = lambda size: self.generate_pandas_df(size=size)
    microbatch_def = lambda: self.actual_dataframe
    return FileBatchWriter(df_callable, microbatch_def)
   

  def _stream_writer(self):
    df_callable = lambda size: self.generate_pandas_df(size=size)
    microbatch_def = lambda: self.actual_dataframe
    return FileStreamWriter(df_callable, microbatch_def)



class SparkGenerator:

  def __init__(self, spark, F, metadata):
    self.spark = spark
    self.F = F
    self.metadata = metadata
    _size = 0


  def size(self, size):
    self._size = size
    return self


  def get_df(self):
    dataframe = self.spark.range(self._size)
    for k, v in self.metadata.items():
      dataframe = v["method"](self.spark, F=self.F, df=dataframe, col_name=k, **v["kwargs"])
    return dataframe
  

if __name__ == '__main__':

  pass
