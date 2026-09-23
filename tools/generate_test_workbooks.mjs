import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = process.argv[2];
const rowCount = 15_000;
if (!outputDir) throw new Error("Uso: node tools/generate_test_workbooks.mjs <diretorio-de-saida>");

const firstNames = ["Ana", "João", "Maria", "Carlos", "Lívia", "Rafael", "Débora", "Caio", "Renata", "José", "Iara", "Bruno", "Sônia", "Davi", "Érica"];
const lastNames = ["Silva", "Santos", "Oliveira", "Pereira", "Costa", "Almeida", "Ferreira", "Gomes", "Azevedo", "Moura", "D'Ávila", "O'Neil", "Araújo", "Nóbrega"];
const streets = ["Rua São João", "Avenida Brasil", "Travessa das Acácias", "Rua do Sol", "Alameda dos Ipês", "Rua da Liberdade", "Avenida Afonso Pena", "Rua O'Connor"];

function checkDigit(value, weight) {
  let total = 0;
  for (const char of value) { total += Number(char) * weight; weight -= 1; }
  const digit = (total * 10) % 11;
  return digit === 10 ? 0 : digit;
}
function validCpf(seed, withLeadingZero = false) {
  const prefix = withLeadingZero ? `0${String(10_000_000 + (seed % 89_999_999)).padStart(8, "0")}` : String(100_000_000 + (seed % 899_999_999));
  const firstDigit = checkDigit(prefix, 10);
  const secondDigit = checkDigit(`${prefix}${firstDigit}`, 11);
  return `${prefix}${firstDigit}${secondDigit}`;
}
function formatCpf(cpf) { return `${cpf.slice(0, 3)}.${cpf.slice(3, 6)}.${cpf.slice(6, 9)}-${cpf.slice(9)}`; }
function nameFor(index) {
  const base = `${firstNames[index % firstNames.length]} ${lastNames[(index * 3) % lastNames.length]}`;
  switch (index % 9) {
    case 0: return ` ${base.toUpperCase()} `;
    case 1: return base.toLowerCase();
    case 2: return `  ${base}  `;
    case 3: return `'${base}`;
    case 4: return `${base}'`;
    case 5: return `"${base}"`;
    case 6: return `${firstNames[index % firstNames.length]} "Teste" ${lastNames[(index * 3) % lastNames.length]}`;
    case 7: return `${firstNames[index % firstNames.length]}   ${lastNames[(index * 3) % lastNames.length]}`;
    default: return base;
  }
}
function rowFor(index) {
  const pattern = index % 25;
  const cpf = validCpf(index + 1_000, pattern === 6);
  let rawCpf = pattern % 3 === 0 ? formatCpf(cpf) : cpf;
  if (pattern === 6) rawCpf = Number(cpf.slice(1));
  const emailLocal = `cadastro${String(index + 1).padStart(5, "0")}`;
  const phone = `(${String(11 + (index % 80)).padStart(2, "0")}) 9${String(1000 + (index % 9000)).padStart(4, "0")}-${String(1000 + ((index * 7) % 9000)).padStart(4, "0")}`;
  const address = ` ${streets[index % streets.length]}, ${10 + (index % 9000)} - Bairro ${index % 200} `;
  const row = [nameFor(index), rawCpf, pattern % 5 === 0 ? ` ${emailLocal.toUpperCase()}@EXAMPLE.COM ` : `${emailLocal}@example.com`, pattern % 4 === 0 ? phone.replace(/[() -]/g, "") : phone, pattern % 7 === 0 ? address.replace(" - ", "   -   ") : address, pattern % 8 === 0 ? "sim" : "SIM"];
  if (pattern === 19) row[1] = "111.111.111-11";
  if (pattern === 20) row[2] = `cadastro${index + 1}@@example.com`;
  if (pattern === 21) row[3] = "123";
  if (pattern === 22) row[4] = "";
  if (pattern === 23) row[5] = "Não";
  if (pattern === 24) row[5] = "Talvez";
  return row;
}

const headers = [[" NOME COMPLETO ", " C.P.F. ", "E-mail", "Telefone ", "Endereço", "Aceita LGPD (SIM, Não)"]];
const rows = Array.from({ length: rowCount }, (_, index) => rowFor(index));
await fs.mkdir(outputDir, { recursive: true });
const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Cadastro");
sheet.showGridLines = false;
sheet.getRangeByIndexes(0, 0, rowCount + 1, 6).values = [...headers, ...rows];
const used = sheet.getRange(`A1:F${rowCount + 1}`);
used.format.font = { name: "Arial", size: 10, color: "#1F2937" };
used.format.verticalAlignment = "center";
sheet.getRange("A1:F1").format = { fill: "#1F4E78", font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" }, wrapText: true };
sheet.getRange(`A2:F${rowCount + 1}`).format.borders = { preset: "insideHorizontal", style: "thin", color: "#E5E7EB" };
sheet.getRange("A:A").format.columnWidth = 30;
sheet.getRange("B:B").format.columnWidth = 18;
sheet.getRange("C:C").format.columnWidth = 34;
sheet.getRange("D:D").format.columnWidth = 20;
sheet.getRange("E:E").format.columnWidth = 42;
sheet.getRange("F:F").format.columnWidth = 26;
sheet.getRange(`B2:B${rowCount + 1}`).format.numberFormat = "@";
sheet.freezePanes.freezeRows(1);
sheet.tables.add(`A1:F${rowCount + 1}`, true, "CadastroFicticioTable");
workbook.recalculate();
console.log((await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 1800, tableMaxRows: 4, tableMaxCols: 6 })).ndjson);
console.log((await workbook.inspect({ kind: "region", sheetId: "Cadastro", range: `A${rowCount - 1}:F${rowCount + 1}`, maxChars: 1800 })).ndjson);
console.log((await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" })).ndjson);
const preview = await workbook.render({ sheetName: "Cadastro", range: "A1:F22", scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/cadastro_ficticio_preview.png`, new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/cadastro_ficticio_malformatado.xlsx`);
