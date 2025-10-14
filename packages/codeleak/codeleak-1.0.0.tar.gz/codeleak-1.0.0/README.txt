codeleak: Pack & Reveal Utility
===============================

Usage:
  Pack   : codeleak --pack {INPUT_DIR} {OUTPUT_DIR} {SIZE}
  Reveal : codeleak --reveal {INPUT_DIR} {OUTPUT_DIR}

Example:
  codeleak -p 00_source 01_compressed 1K 
  codeleak -r 01_compressed 02_decompressed 

Description:
  - PACK  : Create .tar.gz from INPUT_DIR, convert to HEX, split into chunks.
  - REVEAL: Combine HEX parts, restore .tar.gz, and extract to OUTPUT_DIR.
