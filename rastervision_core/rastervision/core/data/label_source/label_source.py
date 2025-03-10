from typing import TYPE_CHECKING, Any, Optional
from abc import ABC, abstractmethod, abstractproperty

if TYPE_CHECKING:
    from rastervision.core.box import Box
    from rastervision.core.data import CRSTransformer, Labels


class LabelSource(ABC):
    """An interface for storage of labels for a scene.

    A LabelSource is a read-only source of labels for a scene
    that could be backed by a file, a database, an API, etc. The difference
    between LabelSources and Labels can be understood by analogy to the
    difference between a database and result sets queried from a database.
    """

    @abstractmethod
    def get_labels(self, window: Optional['Box'] = None) -> 'Labels':
        """Return labels overlapping with window.

        Args:
            window: Box

        Returns:
            Labels overlapping with window. If window is None,
                returns all labels.
        """
        pass

    @abstractproperty
    def extent(self) -> 'Box':
        pass

    @abstractproperty
    def crs_transformer(self) -> 'CRSTransformer':
        pass

    @abstractmethod
    def set_extent(self, extent: 'Box') -> None:
        """Set self.extent to the given value.

        .. note:: This method is idempotent.

        Args:
            extent (Box): User-specified extent in pixel coordinates.
        """
        pass

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, Box):
            raise NotImplementedError()
        elif isinstance(key, slice):
            key = [key]
        elif isinstance(key, tuple):
            pass
        else:
            raise TypeError('Unsupported key type.')
        slices = list(key)
        assert 1 <= len(slices) <= 2
        assert all(s is not None for s in slices)
        assert isinstance(slices[0], slice)
        if len(slices) == 1:
            h, = slices
            w = slice(None, None)
        else:
            assert isinstance(slices[1], slice)
            h, w = slices

        if any(x is not None and x < 0
               for x in [h.start, h.stop, w.start, w.stop]):
            raise NotImplementedError()

        ymin, xmin, ymax, xmax = self.extent
        _ymin = 0 if h.start is None else h.start
        _xmin = 0 if w.start is None else w.start
        _ymax = ymax if h.stop is None else h.stop
        _xmax = xmax if w.stop is None else w.stop
        window = Box(_ymin, _xmin, _ymax, _xmax)
        return self[window]
