#!/usr/bin/env bash
# Abre o .docx no Microsoft Word (macOS), atualiza sumário, listas e campos, salva e exporta o PDF.
# O Word é "sandboxed": o arquivo passa por uma pasta dentro do contêiner dele.
set -euo pipefail
cd "$(dirname "$0")/../.."
NOME=${1:-PIM_Torre_Solar_v1}
W="$HOME/Library/Containers/com.microsoft.Word/Data/pim_relatorio"
mkdir -p "$W"; rm -f "$W/$NOME".*
cp "docs/relatorio/$NOME.docx" "$W/"
osascript -e 'tell application "Microsoft Word" to close every document saving no' >/dev/null 2>&1 || true
open -a "Microsoft Word" "$W/$NOME.docx"
for _ in $(seq 1 30); do
  [ "$(osascript -e 'tell application "Microsoft Word" to count documents' 2>/dev/null)" != "0" ] && break; sleep 2
done
sleep 3
osascript <<OSA
tell application "Microsoft Word"
	set d to document 1
	set n to count of tables of contents of d
	repeat 2 times
		try
			update fields of text object of d
		end try
		repeat with i from 1 to n
			update table of contents i of d
		end repeat
	end repeat
	save d
	save as d file name "$W/$NOME.pdf" file format format PDF
	close d saving no
end tell
OSA
cp "$W/$NOME.docx" "$W/$NOME.pdf" docs/relatorio/
echo "OK docs/relatorio/$NOME.pdf ($(pdfinfo "docs/relatorio/$NOME.pdf" | awk '/Pages/{print $2}') páginas)"
