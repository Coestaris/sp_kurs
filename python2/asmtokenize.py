import re
import asmfirstpass
import asmsecondpass
from asmtypes import *

directives = [".DATA", ".CODE", ".MODEL", "END", "DB", "DD"]
instructions = ["STD", "JNGE", "JMP", "PUSH", "POP", "IDIV", "ADD", "ADC", "IN", "OR"]
registers32 = ["EAX", "EBX", "ECX", "EDX", "EBP", "ESP", "ESI", "EDI"]
registers8 = ["AL", "BL", "DL", "CL", "AH", "BH", "DH", "CH"]
registers_seg = ["CS", "FS", "DS", "ES", "SS", "GS"]
models = ["SMALL", "TINY"]
splitters = [":", " ", "[", "]", "\n", "\t", ","]

dec_re = re.compile(r"^-?[0-9]+$")
bin_re = re.compile(r"^-?[01]+B$")
string_re = re.compile(r"^\'.+\'$")
id_re = re.compile(r"^[A-Z]\w{,3}$")


def type_detector(string_token):
    if string_token in directives:
        return TokenType.directive

    elif string_token in registers32:
        return TokenType.register32

    elif string_token in registers8:
        return TokenType.register8

    elif string_token in registers_seg:
        return TokenType.register_seg

    elif string_token in models:
        return TokenType.model

    elif string_token in instructions:
        return TokenType.instruction

    elif string_token in splitters:
        return TokenType.splitter

    elif re.fullmatch(string_re, string_token):
        return TokenType.string

    elif re.fullmatch(dec_re, string_token):
        return TokenType.dec_number

    elif re.fullmatch(bin_re, string_token):
        return TokenType.bin_number

    elif re.fullmatch(id_re, string_token):
        return TokenType.user_type

    else:
        return TokenType.unknown


STRING_TYPES = {
    TokenType.directive: "DIRECTIVE",
    TokenType.register32: "REGISTER32",
    TokenType.register8: "REGISTER8",
    TokenType.register_seg: "REGISTER_SEG",
    TokenType.model: "MODEL",
    TokenType.data_type: "DIRECTIVE",
    TokenType.instruction: "INSTRUCTION",
    TokenType.splitter: "SPLITTER",
    TokenType.dec_number: "DEC_NUMBER",
    TokenType.bin_number: "BIN_NUBMER",
    TokenType.user_type: "USER_NAME",
    TokenType.string: "STRING",
    TokenType.unknown: "UNKNOWN"
}


def proceed_token(tokens, token, line_index, storage):
    if len(token.strip()) != 0:
        type = type_detector(token)
        if type == TokenType.unknown:
            storage.set_error(line_index, "Unknown token format of {}".format(token))
            return False
        tokens.append(Token(type, token, line_index))
    return True


def get_line_tokens(line, storage, line_index):
    tokens = []
    token = ""
    is_string = False
    for char in line:
        if char == '\'':
            is_string = not is_string

        if is_string:
            token += char
            continue

        if char in splitters:
            if not proceed_token(tokens, token, line_index, storage):
                return (tokens, False)
            if not proceed_token(tokens, char, line_index, storage):
                return (tokens, False)
            token = ""

        else:
            token += char.upper()

    if not proceed_token(tokens, token, line_index, storage):
        return (tokens, False)
    return (tokens, True)


def get_line_structure(tokens, storage, line_index):
    structure = LineStructure()

    if len(tokens) == 0:
        return structure, True

    offset = 0
    if tokens[0].type == TokenType.user_type:
        structure.has_name = True
        offset = 1
        if len(tokens) > 1 and tokens[1].value == ":":
            offset = 2

    # Only name or label presents
    if offset == len(tokens):
        if offset == 1:
            storage.set_error(line_index, "Name without instruction")
            return structure, False
        return structure, True

    if tokens[offset].type == TokenType.instruction or tokens[offset].type == TokenType.directive:

        if tokens[offset].type == TokenType.instruction and offset == 1:
            storage.set_error(line_index, "Named instructions are not allowed")
            return structure, False

        structure.instruction_index = offset
        structure.has_instruction = True
        offset += 1
    else:
        storage.set_error(line_index, "Instruction expected")
        return structure, False

    # No parameters
    if offset == len(tokens):
        return structure, True

    coma_index = -1
    for index, token in enumerate(tokens):
        if token.value == ",":
            coma_index = index
            break

    structure.op1_index = offset
    if coma_index == -1:
        # 1 parameter
        structure.op1_len = len(tokens) - offset
        structure.op_count = 1
    else:
        # 2 parameters
        structure.op1_len = coma_index - offset
        structure.op2_index = coma_index + 1
        structure.op2_len = len(tokens) - coma_index - 1
        structure.op_count = 2

    return structure, True


def get_lexeme_type(tokens, structure):
    if len(tokens) == 0:
        return LexemeType.blank

    if len(tokens) == 2 and tokens[0].value == ".MODEL" and tokens[1].type == TokenType.model:
        return LexemeType.model

    if len(tokens) == 1 and tokens[0].value == ".DATA":
        return LexemeType.data_seg

    if len(tokens) == 1 and tokens[0].value == ".CODE":
        return LexemeType.code_seg

    if len(tokens) == 1 and tokens[0].value == "END":
        return LexemeType.end

    if len(tokens) == 2 and tokens[0].type == TokenType.user_type and tokens[1].value == ":":
        return LexemeType.label

    if len(tokens) >= 1 and tokens[0].type == TokenType.instruction:
        return LexemeType.instruction

    if len(tokens) == 3 and tokens[0].type == TokenType.user_type and \
            (tokens[1].value == "DB" or tokens[1].value == "DD") and \
            (tokens[2].type == TokenType.bin_number or tokens[2].type == TokenType.dec_number or tokens[
                2].type == TokenType.string):
        return LexemeType.var_def

    return LexemeType.unknown


def print_tokens(tokens, out_file):
    result = ""
    for i, token in enumerate(tokens):
        result += "({} | {} | {}), ".format(token.value, STRING_TYPES[token.type], i + 1)
    print("TOKENS :|" + result, file=out_file)


def print_structure(structure, out_file):
    result = ""
    if structure.has_name:
        result += "| 1 |"
    else:
        result += "| - |"

    if structure.has_instruction:
        result += " {} 1 |".format(structure.instruction_index + 1)
        for op in structure.get_ops():
            result += " {} {} |".format(op[0] + 1, op[1])

    print("STRUCT :|" + result, file=out_file)


def tokenize(in_filename, out_filename, et1_print, et2_print, et3_print):
    try:
        output_file = open(out_filename, "w")
        input_file = open(in_filename)

        storage = Storage(output_file)

        # ETAP2 header output
        if et2_print:
            print("=" * 60, file=output_file)
            print("|  # || OFFSET || SIZE ||           LINE       ", file=output_file)
            print("=" * 60, file=output_file)

        # ETAP3 header output
        if et3_print:
            print("=" * 80, file=output_file)
            print("|  # || OFFSET || SIZE ||         BYTES         ||         LINE       ", file=output_file)
            print("=" * 80, file=output_file)

        global_tokens = {}
        global_types = {}
        global_structures = {}
        global_prototypes = {}

        # Iterating thought all lines for a first time
        for line_index, line in enumerate(input_file):
            line = line.rstrip()

            if et1_print:
                print("LINE   :|" + line, file=output_file)

            tokens, ok = get_line_tokens(line, storage, line_index)
            global_tokens[line_index] = tokens

            if ok:
                structure, ok = get_line_structure(tokens, storage, line_index)
                global_structures[line_index] = structure

            if ok and et1_print:
                print_tokens(tokens, output_file)
                print_structure(structure, output_file)
                print(file=output_file)

            if ok:
                type = get_lexeme_type(tokens, structure)
                global_types[line_index] = type

                if type == LexemeType.unknown:
                    ok = False
                    storage.set_error(line_index, "Unknown lexeme type")

            if ok:
                prototype = asmfirstpass.first_pass(type, tokens, structure, storage, line_index)
                global_prototypes[line_index] = prototype

            if et2_print:
                asmfirstpass.print_line(line, storage, line_index, output_file)

        input_file.seek(0)
        # Iterating thought all lines for a second time
        for line_index, line in enumerate(input_file):
            line = line.rstrip()

            if not storage.has_error(line_index):
                tokens = global_tokens[line_index]
                structure = global_structures[line_index]
                type = global_types[line_index]
                prototype = global_prototypes[line_index]

                asmsecondpass.second_pass(type, prototype, tokens, structure, storage, line_index, output_file)

            asmsecondpass.print_line(line, storage, line_index, output_file)

        # ETAP2 / ETAP3 tables output
        if et2_print or et3_print:
            print("=" * (60 if et2_print else 80), file=output_file)

            print("\nUser defined segments: ", file=output_file)
            asmfirstpass.print_segments(storage, output_file)
            print("\nSegments assignments: ", file=output_file)
            asmfirstpass.print_segment_destinations(storage, output_file)
            print("\nUser defined names: ", file=output_file)
            asmfirstpass.print_user_names(storage, output_file)

    except IOError as error:
        print("Error: Unable to access file: " + error)
