#include <tree_sitter/parser.h>

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#endif

#define LANGUAGE_VERSION 14
#define STATE_COUNT 51
#define LARGE_STATE_COUNT 2
#define SYMBOL_COUNT 24
#define ALIAS_COUNT 0
#define TOKEN_COUNT 19
#define EXTERNAL_TOKEN_COUNT 0
#define FIELD_COUNT 5
#define MAX_ALIAS_SEQUENCE_LENGTH 15
#define PRODUCTION_ID_COUNT 12

enum {
  anon_sym_SLASH = 1,
  anon_sym_go_DOTmod = 2,
  sym_module_path = 3,
  anon_sym_v = 4,
  anon_sym_DOT = 5,
  anon_sym_DASH = 6,
  anon_sym_alpha = 7,
  anon_sym_beta = 8,
  anon_sym_dev = 9,
  anon_sym_pre = 10,
  anon_sym_rc = 11,
  anon_sym_PLUSincompatible = 12,
  anon_sym_COLON = 13,
  sym_hash_version = 14,
  sym_hash = 15,
  sym_number = 16,
  sym_number_with_decimal = 17,
  sym_hex_number = 18,
  sym_checksum_database = 19,
  sym_checksum = 20,
  sym_version = 21,
  sym_checksum_value = 22,
  aux_sym_checksum_database_repeat1 = 23,
};

static const char * const ts_symbol_names[] = {
  [ts_builtin_sym_end] = "end",
  [anon_sym_SLASH] = "/",
  [anon_sym_go_DOTmod] = "go.mod",
  [sym_module_path] = "module_path",
  [anon_sym_v] = "module_version",
  [anon_sym_DOT] = ".",
  [anon_sym_DASH] = "-",
  [anon_sym_alpha] = "alpha",
  [anon_sym_beta] = "beta",
  [anon_sym_dev] = "dev",
  [anon_sym_pre] = "pre",
  [anon_sym_rc] = "rc",
  [anon_sym_PLUSincompatible] = "+incompatible",
  [anon_sym_COLON] = ":",
  [sym_hash_version] = "hash_version",
  [sym_hash] = "hash",
  [sym_number] = "number",
  [sym_number_with_decimal] = "number_with_decimal",
  [sym_hex_number] = "hex_number",
  [sym_checksum_database] = "checksum_database",
  [sym_checksum] = "checksum",
  [sym_version] = "version",
  [sym_checksum_value] = "checksum_value",
  [aux_sym_checksum_database_repeat1] = "checksum_database_repeat1",
};

static const TSSymbol ts_symbol_map[] = {
  [ts_builtin_sym_end] = ts_builtin_sym_end,
  [anon_sym_SLASH] = anon_sym_SLASH,
  [anon_sym_go_DOTmod] = anon_sym_go_DOTmod,
  [sym_module_path] = sym_module_path,
  [anon_sym_v] = anon_sym_v,
  [anon_sym_DOT] = anon_sym_DOT,
  [anon_sym_DASH] = anon_sym_DASH,
  [anon_sym_alpha] = anon_sym_alpha,
  [anon_sym_beta] = anon_sym_beta,
  [anon_sym_dev] = anon_sym_dev,
  [anon_sym_pre] = anon_sym_pre,
  [anon_sym_rc] = anon_sym_rc,
  [anon_sym_PLUSincompatible] = anon_sym_PLUSincompatible,
  [anon_sym_COLON] = anon_sym_COLON,
  [sym_hash_version] = sym_hash_version,
  [sym_hash] = sym_hash,
  [sym_number] = sym_number,
  [sym_number_with_decimal] = sym_number_with_decimal,
  [sym_hex_number] = sym_hex_number,
  [sym_checksum_database] = sym_checksum_database,
  [sym_checksum] = sym_checksum,
  [sym_version] = sym_version,
  [sym_checksum_value] = sym_checksum_value,
  [aux_sym_checksum_database_repeat1] = aux_sym_checksum_database_repeat1,
};

static const TSSymbolMetadata ts_symbol_metadata[] = {
  [ts_builtin_sym_end] = {
    .visible = false,
    .named = true,
  },
  [anon_sym_SLASH] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_go_DOTmod] = {
    .visible = true,
    .named = false,
  },
  [sym_module_path] = {
    .visible = true,
    .named = true,
  },
  [anon_sym_v] = {
    .visible = true,
    .named = true,
  },
  [anon_sym_DOT] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_DASH] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_alpha] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_beta] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_dev] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_pre] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_rc] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_PLUSincompatible] = {
    .visible = true,
    .named = false,
  },
  [anon_sym_COLON] = {
    .visible = true,
    .named = false,
  },
  [sym_hash_version] = {
    .visible = true,
    .named = true,
  },
  [sym_hash] = {
    .visible = true,
    .named = true,
  },
  [sym_number] = {
    .visible = true,
    .named = true,
  },
  [sym_number_with_decimal] = {
    .visible = true,
    .named = true,
  },
  [sym_hex_number] = {
    .visible = true,
    .named = true,
  },
  [sym_checksum_database] = {
    .visible = true,
    .named = true,
  },
  [sym_checksum] = {
    .visible = true,
    .named = true,
  },
  [sym_version] = {
    .visible = true,
    .named = true,
  },
  [sym_checksum_value] = {
    .visible = true,
    .named = true,
  },
  [aux_sym_checksum_database_repeat1] = {
    .visible = false,
    .named = false,
  },
};

enum {
  field_build = 1,
  field_major = 2,
  field_minor = 3,
  field_patch = 4,
  field_pre_release = 5,
};

static const char * const ts_field_names[] = {
  [0] = NULL,
  [field_build] = "build",
  [field_major] = "major",
  [field_minor] = "minor",
  [field_patch] = "patch",
  [field_pre_release] = "pre_release",
};

static const TSFieldMapSlice ts_field_map_slices[PRODUCTION_ID_COUNT] = {
  [1] = {.index = 0, .length = 3},
  [2] = {.index = 3, .length = 4},
  [3] = {.index = 7, .length = 5},
  [4] = {.index = 12, .length = 6},
  [5] = {.index = 18, .length = 5},
  [6] = {.index = 23, .length = 7},
  [7] = {.index = 30, .length = 6},
  [8] = {.index = 36, .length = 8},
  [9] = {.index = 44, .length = 7},
  [10] = {.index = 51, .length = 8},
  [11] = {.index = 59, .length = 9},
};

static const TSFieldMapEntry ts_field_map_entries[] = {
  [0] =
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
  [3] =
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
  [7] =
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
    {field_pre_release, 8},
  [12] =
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
    {field_pre_release, 8},
    {field_pre_release, 9},
  [18] =
    {field_build, 9},
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
  [23] =
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
    {field_pre_release, 8},
    {field_pre_release, 9},
    {field_pre_release, 10},
  [30] =
    {field_build, 10},
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
    {field_pre_release, 8},
  [36] =
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
    {field_pre_release, 8},
    {field_pre_release, 9},
    {field_pre_release, 10},
    {field_pre_release, 11},
  [44] =
    {field_build, 11},
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
    {field_pre_release, 8},
    {field_pre_release, 9},
  [51] =
    {field_build, 12},
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
    {field_pre_release, 8},
    {field_pre_release, 9},
    {field_pre_release, 10},
  [59] =
    {field_build, 13},
    {field_major, 1},
    {field_minor, 3},
    {field_patch, 5},
    {field_pre_release, 7},
    {field_pre_release, 8},
    {field_pre_release, 9},
    {field_pre_release, 10},
    {field_pre_release, 11},
};

static const TSSymbol ts_alias_sequences[PRODUCTION_ID_COUNT][MAX_ALIAS_SEQUENCE_LENGTH] = {
  [0] = {0},
  [1] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [2] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [3] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [4] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [5] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [6] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [7] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [8] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [9] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [10] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
  [11] = {
    [1] = anon_sym_v,
    [2] = anon_sym_v,
    [3] = anon_sym_v,
    [4] = anon_sym_v,
    [5] = anon_sym_v,
  },
};

static const uint16_t ts_non_terminal_alias_map[] = {
  0,
};

static const TSStateId ts_primary_state_ids[STATE_COUNT] = {
  [0] = 0,
  [1] = 1,
  [2] = 2,
  [3] = 3,
  [4] = 4,
  [5] = 5,
  [6] = 6,
  [7] = 7,
  [8] = 8,
  [9] = 9,
  [10] = 10,
  [11] = 11,
  [12] = 12,
  [13] = 13,
  [14] = 14,
  [15] = 15,
  [16] = 16,
  [17] = 17,
  [18] = 18,
  [19] = 19,
  [20] = 20,
  [21] = 21,
  [22] = 22,
  [23] = 23,
  [24] = 24,
  [25] = 25,
  [26] = 26,
  [27] = 27,
  [28] = 28,
  [29] = 29,
  [30] = 30,
  [31] = 31,
  [32] = 32,
  [33] = 33,
  [34] = 34,
  [35] = 35,
  [36] = 36,
  [37] = 37,
  [38] = 38,
  [39] = 39,
  [40] = 40,
  [41] = 41,
  [42] = 42,
  [43] = 43,
  [44] = 44,
  [45] = 45,
  [46] = 46,
  [47] = 47,
  [48] = 48,
  [49] = 49,
  [50] = 50,
};

static bool ts_lex(TSLexer *lexer, TSStateId state) {
  START_LEXER();
  eof = lexer->eof(lexer);
  switch (state) {
    case 0:
      if (eof) ADVANCE(36);
      if (lookahead == '+') ADVANCE(17);
      if (lookahead == '-') ADVANCE(42);
      if (lookahead == '.') ADVANCE(41);
      if (lookahead == '/') ADVANCE(37);
      if (lookahead == ':') ADVANCE(49);
      if (lookahead == 'a') ADVANCE(59);
      if (lookahead == 'b') ADVANCE(57);
      if (lookahead == 'd') ADVANCE(58);
      if (lookahead == 'g') ADVANCE(24);
      if (lookahead == 'h') ADVANCE(3);
      if (lookahead == 'p') ADVANCE(29);
      if (lookahead == 'r') ADVANCE(9);
      if (lookahead == 'v') ADVANCE(40);
      if (lookahead == '\t' ||
          lookahead == '\n' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(0)
      if (('A' <= lookahead && lookahead <= 'F') ||
          ('c' <= lookahead && lookahead <= 'f')) ADVANCE(62);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(54);
      END_STATE();
    case 1:
      if (lookahead == '.') ADVANCE(41);
      if (lookahead == '\t' ||
          lookahead == '\n' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(1)
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(55);
      END_STATE();
    case 2:
      if (lookahead == '.') ADVANCE(22);
      END_STATE();
    case 3:
      if (lookahead == '1') ADVANCE(50);
      END_STATE();
    case 4:
      if (lookahead == 'a') ADVANCE(44);
      END_STATE();
    case 5:
      if (lookahead == 'a') ADVANCE(43);
      END_STATE();
    case 6:
      if (lookahead == 'a') ADVANCE(31);
      END_STATE();
    case 7:
      if (lookahead == 'a') ADVANCE(19);
      if (lookahead == 'b') ADVANCE(15);
      if (lookahead == 'd') ADVANCE(14);
      if (lookahead == 'p') ADVANCE(29);
      if (lookahead == 'r') ADVANCE(9);
      if (lookahead == '\t' ||
          lookahead == '\n' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(7)
      if (lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9')) ADVANCE(56);
      END_STATE();
    case 8:
      if (lookahead == 'b') ADVANCE(20);
      END_STATE();
    case 9:
      if (lookahead == 'c') ADVANCE(47);
      END_STATE();
    case 10:
      if (lookahead == 'c') ADVANCE(26);
      END_STATE();
    case 11:
      if (lookahead == 'd') ADVANCE(38);
      END_STATE();
    case 12:
      if (lookahead == 'e') ADVANCE(46);
      END_STATE();
    case 13:
      if (lookahead == 'e') ADVANCE(48);
      END_STATE();
    case 14:
      if (lookahead == 'e') ADVANCE(32);
      END_STATE();
    case 15:
      if (lookahead == 'e') ADVANCE(30);
      END_STATE();
    case 16:
      if (lookahead == 'h') ADVANCE(5);
      END_STATE();
    case 17:
      if (lookahead == 'i') ADVANCE(23);
      END_STATE();
    case 18:
      if (lookahead == 'i') ADVANCE(8);
      END_STATE();
    case 19:
      if (lookahead == 'l') ADVANCE(27);
      END_STATE();
    case 20:
      if (lookahead == 'l') ADVANCE(13);
      END_STATE();
    case 21:
      if (lookahead == 'm') ADVANCE(28);
      END_STATE();
    case 22:
      if (lookahead == 'm') ADVANCE(25);
      END_STATE();
    case 23:
      if (lookahead == 'n') ADVANCE(10);
      END_STATE();
    case 24:
      if (lookahead == 'o') ADVANCE(2);
      END_STATE();
    case 25:
      if (lookahead == 'o') ADVANCE(11);
      END_STATE();
    case 26:
      if (lookahead == 'o') ADVANCE(21);
      END_STATE();
    case 27:
      if (lookahead == 'p') ADVANCE(16);
      END_STATE();
    case 28:
      if (lookahead == 'p') ADVANCE(6);
      END_STATE();
    case 29:
      if (lookahead == 'r') ADVANCE(12);
      END_STATE();
    case 30:
      if (lookahead == 't') ADVANCE(4);
      END_STATE();
    case 31:
      if (lookahead == 't') ADVANCE(18);
      END_STATE();
    case 32:
      if (lookahead == 'v') ADVANCE(45);
      END_STATE();
    case 33:
      if (lookahead == '\t' ||
          lookahead == '\n' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(33)
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'F') ||
          ('a' <= lookahead && lookahead <= 'f')) ADVANCE(62);
      END_STATE();
    case 34:
      if (lookahead == '\t' ||
          lookahead == '\n' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(34)
      if (lookahead == '+' ||
          ('/' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(52);
      END_STATE();
    case 35:
      if (eof) ADVANCE(36);
      if (lookahead == '\t' ||
          lookahead == '\n' ||
          lookahead == '\r' ||
          lookahead == ' ') SKIP(35)
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(39);
      END_STATE();
    case 36:
      ACCEPT_TOKEN(ts_builtin_sym_end);
      END_STATE();
    case 37:
      ACCEPT_TOKEN(anon_sym_SLASH);
      END_STATE();
    case 38:
      ACCEPT_TOKEN(anon_sym_go_DOTmod);
      END_STATE();
    case 39:
      ACCEPT_TOKEN(sym_module_path);
      if (('-' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          lookahead == '_' ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(39);
      END_STATE();
    case 40:
      ACCEPT_TOKEN(anon_sym_v);
      END_STATE();
    case 41:
      ACCEPT_TOKEN(anon_sym_DOT);
      END_STATE();
    case 42:
      ACCEPT_TOKEN(anon_sym_DASH);
      END_STATE();
    case 43:
      ACCEPT_TOKEN(anon_sym_alpha);
      END_STATE();
    case 44:
      ACCEPT_TOKEN(anon_sym_beta);
      END_STATE();
    case 45:
      ACCEPT_TOKEN(anon_sym_dev);
      END_STATE();
    case 46:
      ACCEPT_TOKEN(anon_sym_pre);
      END_STATE();
    case 47:
      ACCEPT_TOKEN(anon_sym_rc);
      END_STATE();
    case 48:
      ACCEPT_TOKEN(anon_sym_PLUSincompatible);
      END_STATE();
    case 49:
      ACCEPT_TOKEN(anon_sym_COLON);
      END_STATE();
    case 50:
      ACCEPT_TOKEN(sym_hash_version);
      END_STATE();
    case 51:
      ACCEPT_TOKEN(sym_hash);
      END_STATE();
    case 52:
      ACCEPT_TOKEN(sym_hash);
      if (lookahead == '=') ADVANCE(53);
      if (lookahead == '+' ||
          ('/' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'Z') ||
          ('a' <= lookahead && lookahead <= 'z')) ADVANCE(52);
      END_STATE();
    case 53:
      ACCEPT_TOKEN(sym_hash);
      if (lookahead == '=') ADVANCE(51);
      END_STATE();
    case 54:
      ACCEPT_TOKEN(sym_number);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(54);
      if (('A' <= lookahead && lookahead <= 'F') ||
          ('a' <= lookahead && lookahead <= 'f')) ADVANCE(62);
      END_STATE();
    case 55:
      ACCEPT_TOKEN(sym_number);
      if (('0' <= lookahead && lookahead <= '9')) ADVANCE(55);
      END_STATE();
    case 56:
      ACCEPT_TOKEN(sym_number_with_decimal);
      if (lookahead == '.' ||
          ('0' <= lookahead && lookahead <= '9')) ADVANCE(56);
      END_STATE();
    case 57:
      ACCEPT_TOKEN(sym_hex_number);
      if (lookahead == 'e') ADVANCE(60);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'F') ||
          ('a' <= lookahead && lookahead <= 'f')) ADVANCE(62);
      END_STATE();
    case 58:
      ACCEPT_TOKEN(sym_hex_number);
      if (lookahead == 'e') ADVANCE(61);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'F') ||
          ('a' <= lookahead && lookahead <= 'f')) ADVANCE(62);
      END_STATE();
    case 59:
      ACCEPT_TOKEN(sym_hex_number);
      if (lookahead == 'l') ADVANCE(27);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'F') ||
          ('a' <= lookahead && lookahead <= 'f')) ADVANCE(62);
      END_STATE();
    case 60:
      ACCEPT_TOKEN(sym_hex_number);
      if (lookahead == 't') ADVANCE(4);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'F') ||
          ('a' <= lookahead && lookahead <= 'f')) ADVANCE(62);
      END_STATE();
    case 61:
      ACCEPT_TOKEN(sym_hex_number);
      if (lookahead == 'v') ADVANCE(45);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'F') ||
          ('a' <= lookahead && lookahead <= 'f')) ADVANCE(62);
      END_STATE();
    case 62:
      ACCEPT_TOKEN(sym_hex_number);
      if (('0' <= lookahead && lookahead <= '9') ||
          ('A' <= lookahead && lookahead <= 'F') ||
          ('a' <= lookahead && lookahead <= 'f')) ADVANCE(62);
      END_STATE();
    default:
      return false;
  }
}

static const TSLexMode ts_lex_modes[STATE_COUNT] = {
  [0] = {.lex_state = 0},
  [1] = {.lex_state = 35},
  [2] = {.lex_state = 7},
  [3] = {.lex_state = 0},
  [4] = {.lex_state = 0},
  [5] = {.lex_state = 0},
  [6] = {.lex_state = 0},
  [7] = {.lex_state = 35},
  [8] = {.lex_state = 0},
  [9] = {.lex_state = 35},
  [10] = {.lex_state = 0},
  [11] = {.lex_state = 0},
  [12] = {.lex_state = 0},
  [13] = {.lex_state = 0},
  [14] = {.lex_state = 0},
  [15] = {.lex_state = 0},
  [16] = {.lex_state = 0},
  [17] = {.lex_state = 1},
  [18] = {.lex_state = 0},
  [19] = {.lex_state = 0},
  [20] = {.lex_state = 35},
  [21] = {.lex_state = 35},
  [22] = {.lex_state = 0},
  [23] = {.lex_state = 0},
  [24] = {.lex_state = 0},
  [25] = {.lex_state = 0},
  [26] = {.lex_state = 0},
  [27] = {.lex_state = 0},
  [28] = {.lex_state = 0},
  [29] = {.lex_state = 35},
  [30] = {.lex_state = 0},
  [31] = {.lex_state = 0},
  [32] = {.lex_state = 0},
  [33] = {.lex_state = 0},
  [34] = {.lex_state = 33},
  [35] = {.lex_state = 7},
  [36] = {.lex_state = 33},
  [37] = {.lex_state = 1},
  [38] = {.lex_state = 1},
  [39] = {.lex_state = 0},
  [40] = {.lex_state = 0},
  [41] = {.lex_state = 33},
  [42] = {.lex_state = 7},
  [43] = {.lex_state = 0},
  [44] = {.lex_state = 33},
  [45] = {.lex_state = 33},
  [46] = {.lex_state = 0},
  [47] = {.lex_state = 1},
  [48] = {.lex_state = 1},
  [49] = {.lex_state = 0},
  [50] = {.lex_state = 34},
};

static const uint16_t ts_parse_table[LARGE_STATE_COUNT][SYMBOL_COUNT] = {
  [0] = {
    [ts_builtin_sym_end] = ACTIONS(1),
    [anon_sym_SLASH] = ACTIONS(1),
    [anon_sym_go_DOTmod] = ACTIONS(1),
    [anon_sym_v] = ACTIONS(1),
    [anon_sym_DOT] = ACTIONS(1),
    [anon_sym_DASH] = ACTIONS(1),
    [anon_sym_alpha] = ACTIONS(1),
    [anon_sym_beta] = ACTIONS(1),
    [anon_sym_dev] = ACTIONS(1),
    [anon_sym_pre] = ACTIONS(1),
    [anon_sym_rc] = ACTIONS(1),
    [anon_sym_PLUSincompatible] = ACTIONS(1),
    [anon_sym_COLON] = ACTIONS(1),
    [sym_hash_version] = ACTIONS(1),
    [sym_number] = ACTIONS(1),
    [sym_hex_number] = ACTIONS(1),
  },
  [1] = {
    [sym_checksum_database] = STATE(39),
    [sym_checksum] = STATE(7),
    [aux_sym_checksum_database_repeat1] = STATE(7),
    [sym_module_path] = ACTIONS(3),
  },
};

static const uint16_t ts_small_parse_table[] = {
  [0] = 2,
    ACTIONS(7), 1,
      sym_number_with_decimal,
    ACTIONS(5), 5,
      anon_sym_alpha,
      anon_sym_beta,
      anon_sym_dev,
      anon_sym_pre,
      anon_sym_rc,
  [11] = 4,
    ACTIONS(11), 1,
      anon_sym_DOT,
    ACTIONS(13), 1,
      anon_sym_DASH,
    ACTIONS(15), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(9), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [25] = 4,
    ACTIONS(19), 1,
      anon_sym_DOT,
    ACTIONS(21), 1,
      anon_sym_DASH,
    ACTIONS(23), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(17), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [39] = 3,
    ACTIONS(27), 1,
      anon_sym_DASH,
    ACTIONS(29), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(25), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [50] = 3,
    ACTIONS(33), 1,
      anon_sym_DASH,
    ACTIONS(35), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(31), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [61] = 3,
    ACTIONS(3), 1,
      sym_module_path,
    ACTIONS(37), 1,
      ts_builtin_sym_end,
    STATE(9), 2,
      sym_checksum,
      aux_sym_checksum_database_repeat1,
  [72] = 3,
    ACTIONS(41), 1,
      anon_sym_DASH,
    ACTIONS(43), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(39), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [83] = 3,
    ACTIONS(45), 1,
      ts_builtin_sym_end,
    ACTIONS(47), 1,
      sym_module_path,
    STATE(9), 2,
      sym_checksum,
      aux_sym_checksum_database_repeat1,
  [94] = 3,
    ACTIONS(52), 1,
      anon_sym_DASH,
    ACTIONS(54), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(50), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [105] = 2,
    ACTIONS(58), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(56), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [113] = 2,
    ACTIONS(62), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(60), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [121] = 2,
    ACTIONS(66), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(64), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [129] = 2,
    ACTIONS(70), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(68), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [137] = 2,
    ACTIONS(74), 1,
      anon_sym_PLUSincompatible,
    ACTIONS(72), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [145] = 3,
    ACTIONS(76), 1,
      anon_sym_SLASH,
    ACTIONS(78), 1,
      sym_hash_version,
    STATE(29), 1,
      sym_checksum_value,
  [155] = 2,
    ACTIONS(80), 1,
      anon_sym_DOT,
    ACTIONS(82), 1,
      sym_number,
  [162] = 2,
    ACTIONS(78), 1,
      sym_hash_version,
    STATE(20), 1,
      sym_checksum_value,
  [169] = 1,
    ACTIONS(84), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [174] = 1,
    ACTIONS(86), 2,
      ts_builtin_sym_end,
      sym_module_path,
  [179] = 1,
    ACTIONS(88), 2,
      ts_builtin_sym_end,
      sym_module_path,
  [184] = 1,
    ACTIONS(90), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [189] = 2,
    ACTIONS(92), 1,
      anon_sym_v,
    STATE(16), 1,
      sym_version,
  [196] = 1,
    ACTIONS(94), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [201] = 1,
    ACTIONS(96), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [206] = 1,
    ACTIONS(98), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [211] = 1,
    ACTIONS(100), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [216] = 1,
    ACTIONS(102), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [221] = 1,
    ACTIONS(104), 2,
      ts_builtin_sym_end,
      sym_module_path,
  [226] = 1,
    ACTIONS(106), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [231] = 1,
    ACTIONS(108), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [236] = 1,
    ACTIONS(110), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [241] = 1,
    ACTIONS(112), 2,
      anon_sym_SLASH,
      sym_hash_version,
  [246] = 1,
    ACTIONS(114), 1,
      sym_hex_number,
  [250] = 1,
    ACTIONS(116), 1,
      sym_number_with_decimal,
  [254] = 1,
    ACTIONS(118), 1,
      sym_hex_number,
  [258] = 1,
    ACTIONS(120), 1,
      sym_number,
  [262] = 1,
    ACTIONS(122), 1,
      sym_number,
  [266] = 1,
    ACTIONS(124), 1,
      ts_builtin_sym_end,
  [270] = 1,
    ACTIONS(126), 1,
      anon_sym_COLON,
  [274] = 1,
    ACTIONS(128), 1,
      sym_hex_number,
  [278] = 1,
    ACTIONS(130), 1,
      sym_number_with_decimal,
  [282] = 1,
    ACTIONS(132), 1,
      anon_sym_DOT,
  [286] = 1,
    ACTIONS(134), 1,
      sym_hex_number,
  [290] = 1,
    ACTIONS(136), 1,
      sym_hex_number,
  [294] = 1,
    ACTIONS(138), 1,
      anon_sym_go_DOTmod,
  [298] = 1,
    ACTIONS(140), 1,
      sym_number,
  [302] = 1,
    ACTIONS(142), 1,
      sym_number,
  [306] = 1,
    ACTIONS(144), 1,
      anon_sym_DOT,
  [310] = 1,
    ACTIONS(146), 1,
      sym_hash,
};

static const uint32_t ts_small_parse_table_map[] = {
  [SMALL_STATE(2)] = 0,
  [SMALL_STATE(3)] = 11,
  [SMALL_STATE(4)] = 25,
  [SMALL_STATE(5)] = 39,
  [SMALL_STATE(6)] = 50,
  [SMALL_STATE(7)] = 61,
  [SMALL_STATE(8)] = 72,
  [SMALL_STATE(9)] = 83,
  [SMALL_STATE(10)] = 94,
  [SMALL_STATE(11)] = 105,
  [SMALL_STATE(12)] = 113,
  [SMALL_STATE(13)] = 121,
  [SMALL_STATE(14)] = 129,
  [SMALL_STATE(15)] = 137,
  [SMALL_STATE(16)] = 145,
  [SMALL_STATE(17)] = 155,
  [SMALL_STATE(18)] = 162,
  [SMALL_STATE(19)] = 169,
  [SMALL_STATE(20)] = 174,
  [SMALL_STATE(21)] = 179,
  [SMALL_STATE(22)] = 184,
  [SMALL_STATE(23)] = 189,
  [SMALL_STATE(24)] = 196,
  [SMALL_STATE(25)] = 201,
  [SMALL_STATE(26)] = 206,
  [SMALL_STATE(27)] = 211,
  [SMALL_STATE(28)] = 216,
  [SMALL_STATE(29)] = 221,
  [SMALL_STATE(30)] = 226,
  [SMALL_STATE(31)] = 231,
  [SMALL_STATE(32)] = 236,
  [SMALL_STATE(33)] = 241,
  [SMALL_STATE(34)] = 246,
  [SMALL_STATE(35)] = 250,
  [SMALL_STATE(36)] = 254,
  [SMALL_STATE(37)] = 258,
  [SMALL_STATE(38)] = 262,
  [SMALL_STATE(39)] = 266,
  [SMALL_STATE(40)] = 270,
  [SMALL_STATE(41)] = 274,
  [SMALL_STATE(42)] = 278,
  [SMALL_STATE(43)] = 282,
  [SMALL_STATE(44)] = 286,
  [SMALL_STATE(45)] = 290,
  [SMALL_STATE(46)] = 294,
  [SMALL_STATE(47)] = 298,
  [SMALL_STATE(48)] = 302,
  [SMALL_STATE(49)] = 306,
  [SMALL_STATE(50)] = 310,
};

static const TSParseActionEntry ts_parse_actions[] = {
  [0] = {.entry = {.count = 0, .reusable = false}},
  [1] = {.entry = {.count = 1, .reusable = false}}, RECOVER(),
  [3] = {.entry = {.count = 1, .reusable = true}}, SHIFT(23),
  [5] = {.entry = {.count = 1, .reusable = true}}, SHIFT(17),
  [7] = {.entry = {.count = 1, .reusable = true}}, SHIFT(10),
  [9] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 10, .production_id = 4),
  [11] = {.entry = {.count = 1, .reusable = true}}, SHIFT(35),
  [13] = {.entry = {.count = 1, .reusable = true}}, SHIFT(36),
  [15] = {.entry = {.count = 1, .reusable = true}}, SHIFT(33),
  [17] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 9, .production_id = 3),
  [19] = {.entry = {.count = 1, .reusable = true}}, SHIFT(42),
  [21] = {.entry = {.count = 1, .reusable = true}}, SHIFT(34),
  [23] = {.entry = {.count = 1, .reusable = true}}, SHIFT(31),
  [25] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 6, .production_id = 1),
  [27] = {.entry = {.count = 1, .reusable = true}}, SHIFT(2),
  [29] = {.entry = {.count = 1, .reusable = true}}, SHIFT(22),
  [31] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 12, .production_id = 8),
  [33] = {.entry = {.count = 1, .reusable = true}}, SHIFT(44),
  [35] = {.entry = {.count = 1, .reusable = true}}, SHIFT(25),
  [37] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_checksum_database, 1),
  [39] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 11, .production_id = 6),
  [41] = {.entry = {.count = 1, .reusable = true}}, SHIFT(41),
  [43] = {.entry = {.count = 1, .reusable = true}}, SHIFT(28),
  [45] = {.entry = {.count = 1, .reusable = true}}, REDUCE(aux_sym_checksum_database_repeat1, 2),
  [47] = {.entry = {.count = 2, .reusable = true}}, REDUCE(aux_sym_checksum_database_repeat1, 2), SHIFT_REPEAT(23),
  [50] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 8, .production_id = 2),
  [52] = {.entry = {.count = 1, .reusable = true}}, SHIFT(45),
  [54] = {.entry = {.count = 1, .reusable = true}}, SHIFT(27),
  [56] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 11, .production_id = 7),
  [58] = {.entry = {.count = 1, .reusable = true}}, SHIFT(26),
  [60] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 14, .production_id = 11),
  [62] = {.entry = {.count = 1, .reusable = true}}, SHIFT(32),
  [64] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 10, .production_id = 5),
  [66] = {.entry = {.count = 1, .reusable = true}}, SHIFT(30),
  [68] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 12, .production_id = 9),
  [70] = {.entry = {.count = 1, .reusable = true}}, SHIFT(24),
  [72] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 13, .production_id = 10),
  [74] = {.entry = {.count = 1, .reusable = true}}, SHIFT(19),
  [76] = {.entry = {.count = 1, .reusable = true}}, SHIFT(46),
  [78] = {.entry = {.count = 1, .reusable = true}}, SHIFT(40),
  [80] = {.entry = {.count = 1, .reusable = true}}, SHIFT(47),
  [82] = {.entry = {.count = 1, .reusable = true}}, SHIFT(4),
  [84] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 14, .production_id = 10),
  [86] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_checksum, 5),
  [88] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_checksum_value, 3),
  [90] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 7, .production_id = 1),
  [92] = {.entry = {.count = 1, .reusable = true}}, SHIFT(37),
  [94] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 13, .production_id = 9),
  [96] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 13, .production_id = 8),
  [98] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 12, .production_id = 7),
  [100] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 9, .production_id = 2),
  [102] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 12, .production_id = 6),
  [104] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_checksum, 3),
  [106] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 11, .production_id = 5),
  [108] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 10, .production_id = 3),
  [110] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 15, .production_id = 11),
  [112] = {.entry = {.count = 1, .reusable = true}}, REDUCE(sym_version, 11, .production_id = 4),
  [114] = {.entry = {.count = 1, .reusable = true}}, SHIFT(11),
  [116] = {.entry = {.count = 1, .reusable = true}}, SHIFT(6),
  [118] = {.entry = {.count = 1, .reusable = true}}, SHIFT(14),
  [120] = {.entry = {.count = 1, .reusable = true}}, SHIFT(43),
  [122] = {.entry = {.count = 1, .reusable = true}}, SHIFT(49),
  [124] = {.entry = {.count = 1, .reusable = true}},  ACCEPT_INPUT(),
  [126] = {.entry = {.count = 1, .reusable = true}}, SHIFT(50),
  [128] = {.entry = {.count = 1, .reusable = true}}, SHIFT(15),
  [130] = {.entry = {.count = 1, .reusable = true}}, SHIFT(8),
  [132] = {.entry = {.count = 1, .reusable = true}}, SHIFT(38),
  [134] = {.entry = {.count = 1, .reusable = true}}, SHIFT(12),
  [136] = {.entry = {.count = 1, .reusable = true}}, SHIFT(13),
  [138] = {.entry = {.count = 1, .reusable = true}}, SHIFT(18),
  [140] = {.entry = {.count = 1, .reusable = true}}, SHIFT(3),
  [142] = {.entry = {.count = 1, .reusable = true}}, SHIFT(5),
  [144] = {.entry = {.count = 1, .reusable = true}}, SHIFT(48),
  [146] = {.entry = {.count = 1, .reusable = true}}, SHIFT(21),
};

#ifdef __cplusplus
extern "C" {
#endif
#ifdef _WIN32
#define extern __declspec(dllexport)
#endif

extern const TSLanguage *tree_sitter_gosum(void) {
  static const TSLanguage language = {
    .version = LANGUAGE_VERSION,
    .symbol_count = SYMBOL_COUNT,
    .alias_count = ALIAS_COUNT,
    .token_count = TOKEN_COUNT,
    .external_token_count = EXTERNAL_TOKEN_COUNT,
    .state_count = STATE_COUNT,
    .large_state_count = LARGE_STATE_COUNT,
    .production_id_count = PRODUCTION_ID_COUNT,
    .field_count = FIELD_COUNT,
    .max_alias_sequence_length = MAX_ALIAS_SEQUENCE_LENGTH,
    .parse_table = &ts_parse_table[0][0],
    .small_parse_table = ts_small_parse_table,
    .small_parse_table_map = ts_small_parse_table_map,
    .parse_actions = ts_parse_actions,
    .symbol_names = ts_symbol_names,
    .field_names = ts_field_names,
    .field_map_slices = ts_field_map_slices,
    .field_map_entries = ts_field_map_entries,
    .symbol_metadata = ts_symbol_metadata,
    .public_symbol_map = ts_symbol_map,
    .alias_map = ts_non_terminal_alias_map,
    .alias_sequences = &ts_alias_sequences[0][0],
    .lex_modes = ts_lex_modes,
    .lex_fn = ts_lex,
    .primary_state_ids = ts_primary_state_ids,
  };
  return &language;
}
#ifdef __cplusplus
}
#endif
