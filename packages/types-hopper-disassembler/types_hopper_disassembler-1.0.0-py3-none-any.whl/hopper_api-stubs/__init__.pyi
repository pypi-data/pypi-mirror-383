"""
Hopper Disassembler Python API Type Stubs

"""

from typing import List, Optional, Union

__version__: str

class CallReference:
    """
    An object representing a call inside from / to a procedure.

    CALL_NONE       = 0
    CALL_UNKNOWN    = 1
    CALL_DIRECT     = 2
    CALL_OBJC       = 3
    """

    CALL_NONE: int
    CALL_UNKNOWN: int
    CALL_DIRECT: int
    CALL_OBJC: int

    def __init__(self, callType: int, fromAddress: int, toAddress: int) -> None: ...
    def type(self) -> int:
        """
        Returns the type of call. This is one of the value CALL_NONE, CALL_UNKNOWN, CALL_DIRECT, or CALL_OBJC.
        """
        ...

    def fromAddress(self) -> int:
        """
        Source of the reference
        """
        ...

    def toAddress(self) -> int:
        """
        Referenced address
        """
        ...

class LocalVariable:
    """
    A procedure's local variable.
    """

    def __init__(self, name: str, displacement: int) -> None: ...
    def name(self) -> str:
        """
        Name of the local variable
        """
        ...

    def displacement(self) -> int:
        """
        Displacement on the stack
        """
        ...

class Tag:
    """
    A Tag that could be applied to a specific address, a BasicBlock or a Procedure.
    """

    def __init__(self, tag_internal: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def getName(self) -> str:
        """
        Returns a string with the tag name.
        """
        ...

class Procedure:
    """
    This class represents a procedure, which is a collection of BasicBlocks.

    REGCLS_GENERAL_PURPOSE_REGISTER     = 2

    REGCLS_X86_FPU                      = 3
    REGCLS_X86_MMX                      = 4
    REGCLS_X86_SSE                      = 5
    REGCLS_X86_AVX                      = 6
    REGCLS_X86_CR                       = 7
    REGCLS_X86_DR                       = 8
    REGCLS_X86_SPECIAL                  = 9
    REGCLS_X86_MEMMGMT                  = 10
    REGCLS_X86_SEG                      = 11

    REGCLS_ARM_VFP_SINGLE               = 3
    REGCLS_ARM_VFP_DOUBLE               = 4
    REGCLS_ARM_VFP_QUAD                 = 5
    REGCLS_ARM_MEDIA                    = 6
    REGCLS_ARM_SPECIAL                  = 7

    REGIDX_X86_RAX                      = 0
    REGIDX_X86_RCX                      = 1
    REGIDX_X86_RDX                      = 2
    REGIDX_X86_RBX                      = 3
    REGIDX_X86_RSP                      = 4
    REGIDX_X86_RBP                      = 5
    REGIDX_X86_RSI                      = 6
    REGIDX_X86_RDI                      = 7
    REGIDX_X86_R8                       = 8
    REGIDX_X86_R9                       = 9
    REGIDX_X86_R10                      = 10
    REGIDX_X86_R11                      = 11
    REGIDX_X86_R12                      = 12
    REGIDX_X86_R13                      = 13
    REGIDX_X86_R14                      = 14
    REGIDX_X86_R15                      = 15
    REGIDX_X86_RIP                      = 16
    """

    REGCLS_GENERAL_PURPOSE_REGISTER: int
    REGCLS_X86_FPU: int
    REGCLS_X86_MMX: int
    REGCLS_X86_SSE: int
    REGCLS_X86_AVX: int
    REGCLS_X86_CR: int
    REGCLS_X86_DR: int
    REGCLS_X86_SPECIAL: int
    REGCLS_X86_MEMMGMT: int
    REGCLS_X86_SEG: int
    REGCLS_ARM_VFP_SINGLE: int
    REGCLS_ARM_VFP_DOUBLE: int
    REGCLS_ARM_VFP_QUAD: int
    REGCLS_ARM_MEDIA: int
    REGCLS_ARM_SPECIAL: int
    REGIDX_X86_RAX: int
    REGIDX_X86_RCX: int
    REGIDX_X86_RDX: int
    REGIDX_X86_RBX: int
    REGIDX_X86_RSP: int
    REGIDX_X86_RBP: int
    REGIDX_X86_RSI: int
    REGIDX_X86_RDI: int
    REGIDX_X86_R8: int
    REGIDX_X86_R9: int
    REGIDX_X86_R10: int
    REGIDX_X86_R11: int
    REGIDX_X86_R12: int
    REGIDX_X86_R13: int
    REGIDX_X86_R14: int
    REGIDX_X86_R15: int
    REGIDX_X86_RIP: int

    def __init__(self, segment_internal: int, procedure_index: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def getSegment(self) -> "Segment":
        """
        Returns the segment this procedure belongs to.
        """
        ...

    def getSection(self) -> "Section":
        """
        Returns the section this procedure belongs to.
        """
        ...

    def getEntryPoint(self) -> int:
        """
        Returns the address of the entry point.
        """
        ...

    def getBasicBlockCount(self) -> int:
        """
        Returns the total number of basic blocks.
        """
        ...

    def getBasicBlock(self, index: int) -> Optional["BasicBlock"]:
        """
        Get a BasicBlock object by index.
        """
        ...

    def getBasicBlockAtAddress(self, addr: int) -> Optional["BasicBlock"]:
        """
        Returns the basic block which contains an instruction starting at the given address, or None.
        """
        ...

    def basicBlockIterator(self):
        """
        Iterate over all basic blocks of the procedure
        """
        ...

    def getHeapSize(self) -> int:
        """
        Returns the heap size of the procedure in bytes.
        """
        ...

    def getLocalVariableList(self) -> List[LocalVariable]:
        """
        Returns the list of all local variables.
        """
        ...

    def addTag(self, tag: Tag) -> None:
        """
        Add a tag to the procedure.
        """
        ...

    def removeTag(self, tag: Tag) -> None:
        """
        Remove the tag from the procedure.
        """
        ...

    def hasTag(self, tag: Tag) -> bool:
        """
        Returns True if the procedure has this tag.
        """
        ...

    def getTagCount(self) -> int:
        """
        Returns the number of tags for this procedure.
        """
        ...

    def getTagAtIndex(self, index: int) -> Optional[Tag]:
        """
        Returns the Nth tag of the procedure.
        """
        ...

    def tagIterator(self):
        """
        Iterate over all tags of the procedure
        """
        ...

    def getTagList(self) -> List[Tag]:
        """
        Returns a list an all tags for this procedure.
        """
        ...

    def getAllCallers(self) -> List[CallReference]:
        """
        Returns a list of CallReference objects representing callers of this procedure.
        """
        ...

    def getAllCallees(self) -> List[CallReference]:
        """
        Returns a list of CallReference objects representing all the places called by this procedure.
        """
        ...

    def getAllCallerProcedures(self) -> List["Procedure"]:
        """
        Returns a list of Procedure objects representing callers of this procedure.
        """
        ...

    def getAllCalleeProcedures(self) -> List["Procedure"]:
        """
        Returns a list of CallReference objects representing all the procedures called by this procedure.
        """
        ...

    def hasLocalLabelAtAddress(self, addr: int) -> bool:
        """
        Return True if there is a local label at a given address.
        """
        ...

    def localLabelAtAddress(self, addr: int) -> Optional[str]:
        """
        Return the local label name at a given address, or None if there is no label at this address.
        """
        ...

    def setLocalLabelAtAddress(self, label: str, addr: int) -> bool:
        """
        Set the local label for a given address.
        """
        ...

    def declareLocalLabelAt(self, addr: int) -> str:
        """
        Create a local label at a given address, and return its name.
        """
        ...

    def removeLocalLabelAtAddress(self, addr: int) -> bool:
        """
        Remove a local label.
        """
        ...

    def addressOfLocalLabel(self, label: str) -> int:
        """
        Return the address of the local label.
        """
        ...

    def decompile(self) -> Optional[str]:
        """
        Returns a string containing the pseudocode of the procedure, or None if the decompilation is not possible.
        """
        ...

    def signatureString(self) -> str:
        """
        Returns a string containing the signature of the procedure.
        """
        ...

    def renameRegister(self, reg_cls: int, reg_idx: int, name: str) -> bool:
        """
        Rename the register reg_idx, of class reg_cls to the provided name. The reg_cls argument is one of the REGCLS_* constants.
        """
        ...

    def registerNameOverride(self, reg_cls: int, reg_idx: int) -> Optional[str]:
        """
        Returns the name given to the register, if it has been previously renamed. Otherwise, returns None. The reg_cls argument is one of the REGCLS_* constants.
        """
        ...

    def clearRegisterNameOverride(self, reg_cls: int, reg_idx: int) -> bool:
        """
        Clear register renaming. The reg_cls argument is one of the REGCLS_* constants.
        """
        ...

class BasicBlock:
    """
    A BasicBlock is a set of instructions that is guaranteed to be executed in a whole, if the control flow reach the first instruction.
    """

    def __init__(self, procedure: Procedure, basic_block_index: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def getProcedure(self) -> Procedure:
        """
        Returns the Procedure object this BasicBlock belongs to.
        """
        ...

    def getStartingAddress(self) -> int:
        """
        Returns the address of the first instruction of the BasicBlock.
        """
        ...

    def getEndingAddress(self) -> int:
        """
        Returns the address following the last instruction of the BasicBlock.
        """
        ...

    def getSuccessorCount(self) -> int:
        """
        Returns the number of successors for this BasicBlock.
        """
        ...

    def getSuccessorIndexAtIndex(self, index: int) -> int:
        """
        Returns the BasicBlock index of the Nth successors.
        """
        ...

    def getSuccessorAddressAtIndex(self, index: int) -> int:
        """
        Returns the BasicBlock address of the Nth successors.
        """
        ...

    def addTag(self, tag: Tag) -> None:
        """
        Add a tag to the basic block.
        """
        ...

    def removeTag(self, tag: Tag) -> None:
        """
        Remove the tag from the basic block.
        """
        ...

    def hasTag(self, tag: Tag) -> bool:
        """
        Returns True if the basic block has this tag.
        """
        ...

    def getTagCount(self) -> int:
        """
        Return the number of tags for this basic block.
        """
        ...

    def getTagAtIndex(self, index: int) -> Optional[Tag]:
        """
        Return the Nth tag of the basic block.
        """
        ...

    def tagIterator(self):
        """
        Iterate over all tags of the basic block
        """
        ...

    def getTagList(self) -> List[Tag]:
        """
        Return a list an all tags for this basic block.
        """
        ...

class Instruction:
    """
    This class represents a disassembled instruction.

    ARCHITECTURE_UNKNOWN = 0
    ARCHITECTURE_i386 = 1
    ARCHITECTURE_X86_64 = 2
    ARCHITECTURE_ARM = 3
    ARCHITECTURE_ARM_THUMB = 4
    ARCHITECTURE_AARCH64 = 5
    ARCHITECTURE_OTHER = 99
    """

    ARCHITECTURE_UNKNOWN: int
    ARCHITECTURE_i386: int
    ARCHITECTURE_X86_64: int
    ARCHITECTURE_ARM: int
    ARCHITECTURE_ARM_THUMB: int
    ARCHITECTURE_AARCH64: int
    ARCHITECTURE_OTHER: int

    def __init__(
        self,
        archi: int,
        instr: str,
        rawArgs: List[str],
        formattedArgs: List[str],
        cjmp: bool,
        ijmp: bool,
        instrLen: int,
    ) -> None: ...
    @staticmethod
    def stringForArchitecture(t: int) -> str:
        """
        Helper method which converts one of the architecture value (ARCHITECTURE_UNKNOWN, ARCHITECTURE_i386,
        ARCHITECTURE_X86_64, ARCHITECTURE_ARM, ARCHITECTURE_ARM_THUMB, or  ARCHITECTURE_AARCH64) to a string value.
        """
        ...

    def getArchitecture(self) -> int:
        """
        Returns the architecture.
        """
        ...

    def getInstructionString(self) -> str:
        """
        Return a strings representing the instruction.
        """
        ...

    def getArgumentCount(self) -> int:
        """
        Returns the number of argument.
        """
        ...

    def getRawArgument(self, index: int) -> Optional[str]:
        """
        Returns the instruction argument, identified by an index. The argument is not modified by Hopper, and represents the raw ASM argument.
        """
        ...

    def getFormattedArgument(self, index: int) -> Optional[str]:
        """
        Returns the instruction argument, identified by an index. The argument may have been modified according to the user, or by Hopper if
        """
        ...

    def isAnInconditionalJump(self) -> bool:
        """
        Returns True if the instruction represents an inconditional jump.
        """
        ...

    def isAConditionalJump(self) -> bool:
        """
        Returns True if the instruction represents a conditional jump.
        """
        ...

    def getInstructionLength(self) -> int:
        """
        Returns the instruction length in byte.
        """
        ...

class Section:
    """
    This class represents a section of a segment.
    """

    def __init__(self, addr: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def getName(self) -> str:
        """
        Returns the name of the section.
        """
        ...

    def getStartingAddress(self) -> int:
        """
        Returns the starting address of the section.
        """
        ...

    def getLength(self) -> int:
        """
        Returns the length, in bytes, of the section.
        """
        ...

    def getFlags(self) -> int:
        """
        Returns the flags of the section.
        """
        ...

class Segment:
    """
    This class represents a segment of a disassembled file.

    The class defines some values that are used as the type of bytes of the disassembled file.

    TYPE_UNDEFINED : an undefined byte
    TYPE_OUTSIDE : the byte is not in a mapped section
    TYPE_NEXT : a byte that is part of a larger data type (ex, the second byte of a 4 bytes integer...)
    TYPE_INT8 : an integer of a single byte
    TYPE_INT16 : an integer of 2 bytes
    TYPE_INT32 : an integer of 4 bytes
    TYPE_INT64 : an integer of 8 bytes
    TYPE_ASCII : an ASCII string
    TYPE_ALIGN : an alignment
    TYPE_UNICODE : a UNICODE string
    TYPE_CODE : an instruction
    TYPE_PROCEDURE : a procedure

    The class defines the constant BAD_ADDRESS which is returned by some methods when the requested information is incorrect.
    """

    BAD_ADDRESS: int
    TYPE_UNDEFINED: int
    TYPE_OUTSIDE: int
    TYPE_NEXT: int
    TYPE_INT8: int
    TYPE_INT16: int
    TYPE_INT32: int
    TYPE_INT64: int
    TYPE_ASCII: int
    TYPE_UNICODE: int
    TYPE_ALIGN: int
    TYPE_CODE: int
    TYPE_PROCEDURE: int
    TYPE_STRUCTURE: int

    @staticmethod
    def stringForType(t: int) -> str:
        """
        Helper method that converts one of the type value (TYPE_UNDEFINED, TYPE_NEXT, ...) to a string value.
        """
        ...

    def __init__(self, addr: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def getName(self) -> str:
        """
        Returns the name of the segment.
        """
        ...

    def getStartingAddress(self) -> int:
        """
        Returns the starting address of the segment.
        """
        ...

    def getLength(self) -> int:
        """
        Returns the length, in bytes, of the segment.
        """
        ...

    def getFileOffset(self) -> int:
        """
        Returns the file offset of the beginning of the segment.
        """
        ...

    def getFileOffsetForAddress(self, addr: int) -> int:
        """
        Returns the file offset of a particular address.
        """
        ...

    def getSectionCount(self) -> int:
        """
        Returns the number of section this segment contains.
        """
        ...

    def getSection(self, index: int) -> Optional[Section]:
        """
        Returns a section by index. The returned object is an instance of the Section class. If the index of not in the range count, the function returns None.

        """
        ...

    def getSectionsList(self) -> List[Section]:
        """
        Returns a list containing all the sections.
        """
        ...

    def getSectionIndexAtAddress(self, addr: int) -> int:
        """
        Returns the section index for a particular address.
        """
        ...

    def getSectionAtAddress(self, addr: int) -> Optional[Section]:
        """
        Returns the section for a particular address.
        """
        ...

    def readBytes(self, addr: int, length: int) -> Union[bytes, bool]:
        """
        Read bytes at a given address range. Returns False if the byte is read outside the segment.
        """
        ...

    def readByte(self, addr: int) -> Union[int, bool]:
        """
        Read a byte (between 0..255), read at a given address. Returns False if the byte is read outside the segment.
        """
        ...

    def readUInt16LE(self, addr: int) -> int:
        """
        Read a 16 bits little endian integer.
        """
        ...

    def readUInt32LE(self, addr: int) -> int:
        """
        Read a 32 bits little endian integer.
        """
        ...

    def readUInt64LE(self, addr: int) -> int:
        """
        Read a 64 bits little endian integer.
        """
        ...

    def readUInt16BE(self, addr: int) -> int:
        """
        Read a 16 bits big endian integer.
        """
        ...

    def readUInt32BE(self, addr: int) -> int:
        """
        Read a 32 bits big endian integer.
        """
        ...

    def readUInt64BE(self, addr: int) -> int:
        """
        Read a 64 bits big endian integer.
        """
        ...

    def writeBytes(self, addr: int, bytesStr: bytes) -> bool:
        """
        Write bytes at a given address. Bytes are given as 'bytes'. Returns True if the writing has succeeded.
        """
        ...

    def writeByte(self, addr: int, value: int) -> bool:
        """
        Write a byte at a given address. Returns True if the writing has succeeded.
        """
        ...

    def writeUInt16LE(self, addr: int, value: int) -> bool:
        """
        Write a 16 bits little endian integer. Returns True if succeeded.
        """
        ...

    def writeUInt32LE(self, addr: int, value: int) -> bool:
        """
        Write a 32 bits little endian integer. Returns True if succeeded.
        """
        ...

    def writeUInt64LE(self, addr: int, value: int) -> bool:
        """
        Write a 64 bits little endian integer. Returns True if succeeded.
        """
        ...

    def writeUInt16BE(self, addr: int, value: int) -> bool:
        """
        Write a 16 bits big endian integer. Returns True if succeeded.
        """
        ...

    def writeUInt32BE(self, addr: int, value: int) -> bool:
        """
        Write a 32 bits big endian integer. Returns True if succeeded.
        """
        ...

    def writeUInt64BE(self, addr: int, value: int) -> bool:
        """
        Write a 64 bits big endian integer. Returns True if succeeded.
        """
        ...

    def markAsUndefined(self, addr: int) -> bool:
        """
        Mark the address as being undefined.
        """
        ...

    def markRangeAsUndefined(self, addr: int, length: int) -> bool:
        """
        Mark the address range as being undefined.
        """
        ...

    def markAsCode(self, addr: int) -> bool:
        """
        Mark the address as being code.
        """
        ...

    def markAsProcedure(self, addr: int) -> bool:
        """
        Mark the address as being a procedure.
        """
        ...

    def markAsDataByteArray(self, addr: int, count: int) -> bool:
        """
        Mark the address as being byte array.
        """
        ...

    def markAsDataShortArray(self, addr: int, count: int) -> bool:
        """
        Mark the address as being a short array.
        """
        ...

    def markAsDataIntArray(self, addr: int, count: int) -> bool:
        """
        Mark the address as being an int array.
        """
        ...

    def isThumbAtAddress(self, addr: int) -> bool:
        """
        Returns True is instruction at address addr is ARM Thumb mode.
        """
        ...

    def setThumbModeAtAddress(self, addr: int) -> bool:
        """
        Set the Thumb mode at the given address.
        """
        ...

    def setARMModeAtAddress(self, addr: int) -> bool:
        """
        Set the ARM mode at the given address.
        """
        ...

    def getTypeAtAddress(self, addr: int) -> Optional[int]:
        """
        Returns the type of the byte at a given address.
        """
        ...

    def setTypeAtAddress(self, addr: int, length: int, typeValue: int) -> bool:
        """
        Set the type of byte range.
        """
        ...

    def makeAlignment(self, addr: int, size: int) -> bool:
        """
        Create an alignment at a given address so that the next address is a multiple of size.
        """
        ...

    def getNextAddressWithType(self, addr: int, typeValue: int) -> int:
        """
        Returns the next address of a given type.
        """
        ...

    def disassembleWholeSegment(self) -> bool:
        """
        Disassemble the whole segment.
        """
        ...

    def setNameAtAddress(self, addr: int, name: str) -> bool:
        """
        Set the label name at a given address.
        """
        ...

    def getNameAtAddress(self, addr: int) -> Optional[str]:
        """
        Get the label name at a given address.
        """
        ...

    def getDemangledNameAtAddress(self, addr: int) -> Optional[str]:
        """
        Get the demangled label name at a given address.
        """
        ...

    def getCommentAtAddress(self, addr: int) -> Optional[str]:
        """
        Get the prefix comment at a given address.
        """
        ...

    def setCommentAtAddress(self, addr: int, comment: str) -> bool:
        """
        Set the prefix comment at a given address.
        """
        ...

    def getInlineCommentAtAddress(self, addr: int) -> Optional[str]:
        """
        Get the inline comment at a given address.
        """
        ...

    def setInlineCommentAtAddress(self, addr: int, comment: str) -> bool:
        """
        Set the inline comment at a given address.
        """
        ...

    def getInstructionAtAddress(self, addr: int) -> Optional[Instruction]:
        """
        Get the disassembled instruction at a given address.
        """
        ...

    def getReferencesOfAddress(self, addr: int) -> List[int]:
        """
        Get the list of addresses that reference a given address.
        """
        ...

    def getReferencesFromAddress(self, addr: int) -> List[int]:
        """
        Get the list of addresses referenced by a given address.
        """
        ...

    def addReference(self, addr: int, referenced: int) -> bool:
        """
        Add a cross-reference to the 'referenced' address from 'addr' address.
        """
        ...

    def removeReference(self, addr: int, referenced: int) -> bool:
        """
        Remove the cross-reference to the 'referenced' address from 'addr' address.
        """
        ...

    def getLabelCount(self) -> int:
        """
        Get the number of named addresses.
        """
        ...

    def getLabelName(self, index: int) -> str:
        """
        Get a label name by index.
        """
        ...

    def labelIterator(self):
        """
        Iterate over all the labels of a segment.
        """
        ...

    def getLabelsList(self) -> List[str]:
        """
        Returns a list with all the label of a segment.
        """
        ...

    def getNamedAddresses(self) -> List[int]:
        """
        Returns a list of all addresses with a label name. The list has the same order as the list returned by getLabelsList.
        """
        ...

    def getProcedureCount(self) -> int:
        """
        Returns the number of procedures that has been defined in this segment.
        """
        ...

    def getProcedureAtIndex(self, index: int) -> Procedure:
        """
        Returns the Nth Procedure object of the segment.
        """
        ...

    def getProcedureIndexAtAddress(self, address: int) -> int:
        """
        Returns the index of the procedure at a given address of the segment, or -1 if there is no procedure defined there.
        """
        ...

    def getProcedureAtAddress(self, address: int) -> Optional[Procedure]:
        """
        Returns the Procedure object at a given address of the segment, or None if there is no procedure defined at there.
        """
        ...

    def getInstructionStart(self, address: int) -> int:
        """
        Returns the lowest address value of the instruction found at a particular address. If the given address
        """
        ...

    def getObjectLength(self, address: int) -> int:
        """
        Returns the length in bytes of the object at this address. The object can be an instruction, a data, etc.
        """
        ...

    def isPartOfAnArray(self, address: int) -> bool:
        """
        Returns True if the address is part of an array.
        """
        ...

    def getArrayStartAddress(self, address: int) -> int:
        """
        Returns the array start address, or BAD_ADDRESS if not inside an array.
        """
        ...

    def getArrayElementCount(self, address: int) -> int:
        """
        Returns the number of element in the array, or 0 if not inside an array.
        """
        ...

    def getArrayElementAddress(self, address: int, index: int) -> int:
        """
        Returns the address of the element at the given index, or BAD_ADDRESS if not inside an array.
        """
        ...

    def getArrayElementSize(self, address: int) -> int:
        """
        Returns the size in bytes of a single element of the array, or 0 if not inside an array.
        """
        ...

    def getStringCount(self) -> int:
        """
        Returns the number of strings in the segment.
        """
        ...

    def getStringAtIndex(self, index: int) -> str:
        """
        Return the nth string of the segment.
        """
        ...

    def getStringAddressAtIndex(self, index: int) -> int:
        """
        Return the address of the nth string of the segment.
        """
        ...

    def getStringsList(self) -> List[tuple]:
        """
        Returns a list containing all the strings and there address as a tuple.
        """
        ...

class Document:
    """
    This class represents the disassembled document. A document is a set of segments.

    FORMAT_DEFAULT = 0
    FORMAT_HEXADECIMAL = 1
    FORMAT_DECIMAL = 2
    FORMAT_OCTAL = 3
    FORMAT_CHARACTER = 4
    FORMAT_STACKVARIABLE = 5
    FORMAT_OFFSET = 6
    FORMAT_ADDRESS = 7
    FORMAT_FLOAT = 8
    FORMAT_BINARY = 9

    FORMAT_STRUCTURED = 10
    FORMAT_ENUM = 11
    FORMAT_ADDRESS_DIFF=12

    FORMAT_NEGATE = 0x20
    FORMAT_LEADINGZEROES = 0x40
    FORMAT_SIGNED = 0x80
    """

    FORMAT_DEFAULT: int
    FORMAT_HEXADECIMAL: int
    FORMAT_DECIMAL: int
    FORMAT_OCTAL: int
    FORMAT_CHARACTER: int
    FORMAT_STACKVARIABLE: int
    FORMAT_OFFSET: int
    FORMAT_ADDRESS: int
    FORMAT_FLOAT: int
    FORMAT_BINARY: int
    FORMAT_STRUCTURED: int
    FORMAT_ENUM: int
    FORMAT_ADDRESS_DIFF: int
    FORMAT_NEGATE: int
    FORMAT_LEADINGZEROES: int
    FORMAT_SIGNED: int

    def __init__(self, addr: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    @staticmethod
    def newDocument() -> "Document":
        """
        Creates and returns a new empty document.
        """
        ...

    @staticmethod
    def getCurrentDocument() -> "Document":
        """
        Returns the current document.
        """
        ...

    @staticmethod
    def getAllDocuments() -> List["Document"]:
        """
        Returns a list of all currently opened documents.
        """
        ...

    @staticmethod
    def ask(msg: str) -> Optional[str]:
        """
        Open a window containing a text field, and wait for the user to give a string value. Returns the string, or returns None if the Cancel button is hit.
        """
        ...

    @staticmethod
    def askFile(msg: str, path: Optional[str], save: bool) -> Optional[str]:
        """
        Open a file dialog with a specified title, in order to select a file. The 'save' parameter allows you to choose between on 'open' or a 'save' dialog.
        """
        ...

    @staticmethod
    def askDirectory(msg: str, path: Optional[str]) -> Optional[str]:
        """
        Open a file dialog with a specified title, in order to select a directory.
        """
        ...

    @staticmethod
    def message(msg: str, buttons: List[str]) -> int:
        """
        Open a window containing a text field and a set of buttons. The 'Buttons' parameter is a list of strings. The function returns the index of the clicked button.
        """
        ...

    def closeDocument(self) -> None:
        """
        Close the document.
        """
        ...

    def loadDocumentAt(self, path: str) -> None:
        """
        Load a document at a given path.
        """
        ...

    def saveDocument(self) -> None:
        """
        Save the document.
        """
        ...

    def saveDocumentAt(self, path: str) -> None:
        """
        Save the document at a given path.
        """
        ...

    def getDocumentName(self) -> str:
        """
        Returns the document display name.
        """
        ...

    def setDocumentName(self, name: str) -> None:
        """
        Set the document display name.
        """
        ...

    def backgroundProcessActive(self) -> bool:
        """
        Returns True if the background analysis is still running.
        """
        ...

    def requestBackgroundProcessStop(self) -> None:
        """
        Request the background analysis to stop as soon as possible, and wait for its termination.
        """
        ...

    def waitForBackgroundProcessToEnd(self) -> None:
        """
        Wait until the background analysis is ended.
        """
        ...

    def assemble(self, instr: str, address: int, syntax: int) -> List[int]:
        """
        Assemble an instruction, and returns the bytes as an array. The instruction is NOT injected in the document: the address given to the function is used to encode the instruction. You can use the writeByte method to inject an assembled instruction.
        """
        ...

    def getDatabaseFilePath(self) -> str:
        """
        Returns the path of the current Hopper database for this document (the HOP file).
        """
        ...

    def getExecutableFilePath(self) -> str:
        """
        Returns the path of the executable being analyzed.
        """
        ...

    def setExecutableFilePath(self, path: str) -> bool:
        """
        Set the path of the executable being analyzed.
        """
        ...

    def log(self, msg: str) -> None:
        """
        Display a string message into the log window of the document.
        """
        ...

    def rebase(self, new_base_address: int) -> None:
        """
        Change the file base address.
        """
        ...

    def newSegment(self, start_address: int, length: int) -> Segment:
        """
        Create a new segment of 'length' bytes starting at 'start_address'.
        """
        ...

    def deleteSegment(self, seg_index: int) -> bool:
        """
        Delete the segment at a given index. Return True if succeeded.
        """
        ...

    def renameSegment(self, seg_index: int, name: str) -> bool:
        """
        Rename the segment at a given index. Return True if succeeded.
        """
        ...

    def getSegmentCount(self) -> int:
        """
        Returns the number of segment the document contains.
        """
        ...

    def getSegment(self, index: int) -> Optional[Segment]:
        """
        Returns a segment by index. The returned object is an instance of the Segment class. If the index of not in the range count, the function returns None.
        """
        ...

    def getSegmentByName(self, name: str) -> Optional[Segment]:
        """
        Returns a segment by name. Return None if no segment with this name was found. If multiple segments have this name, the first one is returned.
        """
        ...

    def getSectionByName(self, name: str) -> Optional[Section]:
        """
        Returns a section by name. Return None if no segment with this name was found. If multiple sections have this name, the first one is returned.
        """
        ...

    def getSegmentsList(self) -> List[Segment]:
        """
        Returns a list containing all the segments.
        """
        ...

    def getSegmentIndexAtAddress(self, addr: int) -> int:
        """
        Returns the segment index for a particular address.
        """
        ...

    def getSegmentAtAddress(self, addr: int) -> Optional[Segment]:
        """
        Returns the segment for a particular address.
        """
        ...

    def getSectionAtAddress(self, addr: int) -> Optional[Section]:
        """
        Returns the section for a particular address.
        """
        ...

    def getCurrentSegmentIndex(self) -> int:
        """
        Returns the segment index where the cursor is. Returns -1 if the current segment cannot be located.
        """
        ...

    def getCurrentSegment(self) -> Optional[Segment]:
        """
        Returns the segment where the cursor is. Returns None if the current segment cannot be located.
        """
        ...

    def getCurrentSection(self) -> Optional[Section]:
        """
        Returns the section where the cursor is. Returns None if the current section cannot be located.
        """
        ...

    def getCurrentProcedure(self) -> Optional[Procedure]:
        """
        Returns the Procedure object where the cursor is. Returns None if there is no procedure there.
        """
        ...

    def getCurrentAddress(self) -> int:
        """
        Returns the address where the cursor currently is.
        """
        ...

    def setCurrentAddress(self, addr: int) -> bool:
        """
        Set the address where the cursor currently is.
        """
        ...

    def getSelectionAddressRange(self) -> List[int]:
        """
        Returns a list, containing two addresses. Those address represents the range of bytes covered by the selection.
        """
        ...

    def moveCursorAtAddress(self, addr: int) -> None:
        """
        Move the cursor at a given address.
        """
        ...

    def selectAddressRange(self, addrRange: List[int]) -> None:
        """
        Select a range of byte. The awaited argument is a list containing exactly two address.
        """
        ...

    def getFileOffsetFromAddress(self, addr: int) -> int:
        """
        Returns the file offset corresponding to the given address.
        """
        ...

    def getAddressFromFileOffset(self, offset: int) -> int:
        """
        Returns the address corresponding to the given file offset.
        """
        ...

    def is64Bits(self) -> bool:
        """
        Returns True if the disassembled document is interpreted as a 64 bits binary.
        """
        ...

    def getEntryPoint(self) -> int:
        """
        Returns the entry point of the document.
        """
        ...

    def moveCursorAtEntryPoint(self) -> None:
        """
        Move the cursor at the entry point.
        """
        ...

    def getHighlightedWord(self) -> str:
        """
        Returns the word that is currently highlighted in the assembly view.
        """
        ...

    def setNameAtAddress(self, addr: int, name: str) -> bool:
        """
        Set the label name at a given address.
        """
        ...

    def getNameAtAddress(self, addr: int) -> Optional[str]:
        """
        Get the label name at a given address.
        """
        ...

    def getAddressForName(self, name: str) -> int:
        """
        Get the address associated to a given name.
        """
        ...

    def refreshView(self) -> None:
        """
        Force the assembly view to be refreshed.
        """
        ...

    def moveCursorOneLineDown(self) -> bool:
        """
        Move the current line down, and remove the multiselection if needed. Returns True if cursor moved.
        """
        ...

    def moveCursorOneLineUp(self) -> bool:
        """
        Move the current line up, and remove the multiselection if needed. Returns True if cursor moved.
        """
        ...

    def getRawSelectedLines(self) -> List[str]:
        """
        Returns a list of strings corresponding to the current selection.
        """
        ...

    def addTagAtAddress(self, tag: Tag, addr: int) -> None:
        """
        Add a tag at a particular address.
        """
        ...

    def removeTagAtAddress(self, tag: Tag, addr: int) -> None:
        """
        Remove the tag at a particular address.
        """
        ...

    def hasTagAtAddress(self, tag: Tag, addr: int) -> bool:
        """
        Returns True if the tag is present at this address.
        """
        ...

    def getTagCountAtAddress(self, addr: int) -> int:
        """
        Returns the number of tags at a given address.
        """
        ...

    def getTagAtAddressByIndex(self, addr: int, index: int) -> Optional[Tag]:
        """
        Returns the Nth tag present at a given address.
        """
        ...

    def tagIteratorAtAddress(self, addr: int):
        """
        Iterates over all tags present at a given address.
        """
        ...

    def getTagListAtAddress(self, addr: int) -> List[Tag]:
        """
        Returns the list of all tags present at a given address
        """
        ...

    def getTagCount(self) -> int:
        """
        Returns the total number of tags available.
        """
        ...

    def getTagAtIndex(self, index: int) -> Optional[Tag]:
        """
        Returns a Tag object, or None if the index does not exist.
        """
        ...

    def tagIterator(self):
        """
        Iterate over all the tags.
        """
        ...

    def getTagList(self) -> List[Tag]:
        """
        Returns a list of all tags.
        """
        ...

    def buildTag(self, name: str) -> Tag:
        """
        Build a tag with a given name. If a tag with the same name already exists, it returns the existing tag.
        """
        ...

    def getTagWithName(self, name: str) -> Optional[Tag]:
        """
        Returns a Tag object if a tag with this name already exists, or None.
        """
        ...

    def destroyTag(self, tag: Tag) -> None:
        """
        Remove the tag from every location, and delete it.
        """
        ...

    def hasColorAtAddress(self, addr: int) -> bool:
        """
        Returns True if a color has been defined at the given address.
        """
        ...

    def setColorAtAddress(self, color: int, addr: int) -> bool:
        """
        Sets the color at a given address. The color is a 32bits integer representing the hexadecimal color in the form #AARRGGBB.
        """
        ...

    def getColorAtAddress(self, addr: int) -> int:
        """
        Returns the color at a given address. The color is a 32bits integer representing the hexadecimal color in the form #AARRGGBB.
        """
        ...

    def removeColorAtAddress(self, addr: int) -> None:
        """
        Remove the color at a given address.
        """
        ...

    def readBytes(self, addr: int, length: int) -> Union[bytes, bool]:
        """
        Read bytes from a mapped segment, and return a string. Returns False if no segments was found for this range.
        """
        ...

    def readByte(self, addr: int) -> Union[int, bool]:
        """
        Read a byte from a mapped segment. Returns False if no segments was found for this address.
        """
        ...

    def readUInt16LE(self, addr: int) -> Union[int, bool]:
        """
        Read a 16 bits little endian integer from a mapped segment. Returns False if no segments was found for this address.
        """
        ...

    def readUInt32LE(self, addr: int) -> Union[int, bool]:
        """
        Read a 32 bits little endian integer from a mapped segment. Returns False if no segments was found for this address.
        """
        ...

    def readUInt64LE(self, addr: int) -> Union[int, bool]:
        """
        Read a 64 bits little endian integer from a mapped segment. Returns False if no segments was found for this address.
        """
        ...

    def readUInt16BE(self, addr: int) -> Union[int, bool]:
        """
        Read a 16 bits big endian integer from a mapped segment. Returns False if no segments was found for this address.
        """
        ...

    def readUInt32BE(self, addr: int) -> Union[int, bool]:
        """
        Read a 32 bits big endian integer from a mapped segment. Returns False if no segments was found for this address.
        """
        ...

    def readUInt64BE(self, addr: int) -> Union[int, bool]:
        """
        Read 64 bits bif endian integer from a mapped segment. Returns False if no segments was found for this address.
        """
        ...

    def writeBytes(self, addr: int, byteStr: bytes) -> Union[bool, int]:
        """
        Write bytes to a mapped segment. Bytes are given as a string. Returns False if no segments was found for this range.
        """
        ...

    def writeByte(self, addr: int, value: int) -> Union[bool, int]:
        """
        Write a byte to a mapped segment. Returns True if succeeded.
        """
        ...

    def writeUInt16LE(self, addr: int, value: int) -> Union[bool, int]:
        """
        Write a 16 bits little endian integer to a mapped segment. Returns True if succeeded.
        """
        ...

    def writeUInt32LE(self, addr: int, value: int) -> Union[bool, int]:
        """
        Write a 32 bits little endian integer to a mapped segment. Returns True if succeeded.
        """
        ...

    def writeUInt64LE(self, addr: int, value: int) -> Union[bool, int]:
        """
        Write a 64 bits little endian integer to a mapped segment. Returns True if succeeded.
        """
        ...

    def writeUInt16BE(self, addr: int, value: int) -> Union[bool, int]:
        """
        Write a 16 bits big endian integer to a mapped segment. Returns True if succeeded.
        """
        ...

    def writeUInt32BE(self, addr: int, value: int) -> Union[bool, int]:
        """
        Write a 32 bits big endian integer to a mapped segment. Returns True if succeeded.
        """
        ...

    def writeUInt64BE(self, addr: int, value: int) -> Union[bool, int]:
        """
        Write a 64 bits big endian integer to a mapped segment. Returns True if succeeded.
        """
        ...

    def getOperandFormat(self, addr: int, index: int) -> int:
        """
        Returns the format requested by the user for a given intruction operand.
        """
        ...

    def getOperandFormatRelativeTo(self, addr: int, index: int) -> int:
        """
        Returns the address to which the format is relative. Usually used for FORMAT_ADDRESS_DIFF format.
        """
        ...

    def setOperandFormat(self, addr: int, index: int, fmt: int) -> bool:
        """
        Set the format of a given intruction operand.
        """
        ...

    def setOperandRelativeFormat(self, addr: int, relto: int, index: int, fmt: int) -> bool:
        """
        Set the relative format of a given intruction operand. This version allows one to provide an address
        """
        ...

    def getInstructionStart(self, address: int) -> int:
        """
        Returns the lowest address value of the instruction found at a particular address. If the given address
        """
        ...

    def getObjectLength(self, address: int) -> int:
        """
        Returns the length in bytes of the object at this address. The object can be an instruction, a data, etc.
        """
        ...

    def generateObjectiveCHeader(self) -> bytes:
        """
        Returns a bytearray object containing the generated Objective-C header extracted from the file's metadata.
        """
        ...

    def produceNewExecutable(self, remove_sig: bool = False) -> bytes:
        """
        Produces a new executable including all the modifications.
        """
        ...

    def setBookmarkAtAddress(self, address: int, name: Optional[str] = None) -> bool:
        """
        Set a bookmark at a given address, with an optional name.
        """
        ...

    def removeBookmarkAtAddress(self, address: int) -> bool:
        """
        Removes a bookmark at a given address.
        """
        ...

    def hasBookmarkAtAddress(self, address: int) -> bool:
        """
        Returns True if a bookmark is present at a given address.
        """
        ...

    def renameBookmarkAtAddress(self, address: int, name: str) -> bool:
        """
        Changes the name of an existing bookmark.
        """
        ...

    def findBookmarkWithName(self, name: str) -> List[int]:
        """
        Returns a list of all bookmarks of a given name.
        """
        ...

    def getBookmarkName(self, address: int) -> Optional[str]:
        """
        Returns the name of a bookmark at a given address.
        """
        ...

    def getBookmarks(self) -> List[int]:
        """
        Returns a list of all the addresses with a bookmark.
        """
        ...

class GlobalInformation:
    """
    An object containing various information about the current version of Hopper.
    """

    @staticmethod
    def getHopperMajorVersion() -> int:
        """
        Returns the major version number. If Hopper is at version 4.1.2, it'll return "4".
        """
        ...

    @staticmethod
    def getHopperMinorVersion() -> int:
        """
        Returns the minor version number. If Hopper is at version 4.1.2, it'll return "1".
        """
        ...

    @staticmethod
    def getHopperRevisionNumber() -> int:
        """
        Returns the revision version number. If Hopper is at version 4.1.2, it'll return "2".
        """
        ...

    @staticmethod
    def getHopperVersion() -> str:
        """
        Returns a string with the complete Hopper's version number (ie, something like "4.1.2")
        """
        ...
