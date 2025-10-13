# Copyright 2024 Apheleia
#
# Description:
# Apheleia Verification Library Sequence Item

from __future__ import annotations

from typing import TYPE_CHECKING

from .component import Component
from .sequencer import Sequencer
from .transaction import Transaction

if TYPE_CHECKING:
    from .sequence import Sequence

class SequenceItem(Transaction):
    def __init__(self, name: str, parent: Component) -> None:
        """
        Initializes the SequenceItem with a name and an optional parent component.

        :param name: Name of the sequence item.
        :type name: str
        :param parent: Parent component (optional).
        :type parent: Component
        """
        super().__init__(name, parent)
        self.add_event("done")
        self.add_event("response")

        self._parent_sequence_ = None
        self._parent_sequencer_ = None

        if isinstance(parent, SequenceItem):
            self._parent_sequence_ = parent
            self._parent_sequencer_ = parent.get_sequencer()
        elif isinstance(parent, Sequencer):
            self._parent_sequencer_ = parent

    def set_sequencer(self, sequencer: Sequencer) -> None:
        """
        Sets the sequencer for the item.

        :param sequencer: The sequencer to be set.
        :type sequencer: Sequencer
        """
        self._parent_sequencer_ = sequencer

    def get_sequencer(self) -> Sequencer:
        """
        Gets the sequencer of the item.

        :returns: The sequencer of the item.
        :rtype: Sequencer
        """
        return self._parent_sequencer_

    def set_parent_sequence(self, sequence: Sequence) -> None:
        """
        Sets the parent sequence for the item.

        :param sequence: The parent sequence to be set.
        :type sequence: Sequence
        """
        self._parent_sequence_ = sequence

    def get_parent_sequence(self) -> Sequence:
        """
        Gets the parent sequence of the item.

        :returns: The parent sequence of the item.
        :rtype: Sequence
        """
        return self._parent_sequence_

    def get_root_sequece(self) -> Sequence:
        """
        Gets the root sequence of the item.

        :returns: The root sequence of the item.
        :rtype: Sequence
        """
        retVal = self._parent_sequence_
        while retVal is not None:
            if retVal.parent_sequence is not None:
                retVal = self._parent_sequence_
        return retVal


__all__ = ["SequenceItem"]
