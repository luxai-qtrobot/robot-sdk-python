from typing import TypeVar, Generic, Type, Optional

from luxai.magpie.frames import Frame
from luxai.magpie.transport import StreamReader, StreamWriter

F = TypeVar("F", bound="Frame")

class TypedStreamReader(Generic[F]):
    """
    Represents a stream reader that returns the
    read object with the correct Frame type.
    """

    def __init__(
        self,
        stream_reader: StreamReader,
        frame_type: Type[F],
    ) -> None:
        self.stream_reader = stream_reader
        self._frame_type = frame_type

    def read(self, timeout: Optional[float] = None) -> F:
        """
        Reads data from the stream.
        Args:
            timeout (float, optional): Maximum time to wait for data in seconds.
        Returns:
            F: The data read from the underlying transport, as a Frame subclass.

        Raises:
            TimeoutError: If no data read within the timeout.
            Exception: For transport-level failures.
        """
        data, _ = self.stream_reader.read(timeout=timeout)
        return self._frame_type.from_dict(data=data)      

    def close(self) -> None:
        self.stream_reader.close()      


class TypedStreamWriter(Generic[F]):
    """
    Represents a stream writer that Write data to the stream.    
    """
    def __init__(
        self,
        stream_writer: StreamWriter,
        topic: str        
    ) -> None:        
        self.stream_writer = stream_writer        
        self.topic = topic

    def write(self, data: F) -> None:
        """
        Write data to the stream.
        Args:
            data (Frame): The data to be written to the transport.

        Raises:
            Exception: For transport-level failures.
        """
        self.stream_writer.write(data.to_dict(), self.topic)
      
    def close(self) -> None:
        self.stream_writer.close()