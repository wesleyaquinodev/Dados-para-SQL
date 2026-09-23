import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = process.argv[2];
await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();
const guide = workbook.worksheets.add("LEIA-ME");
const summary = workbook.worksheets.add("Resumo");
const customers = workbook.worksheets.add(" Cadastro de Clientes ");

guide.getRange("A2:F2").merge();
guide.getRange("A2").values = [["Massa fictícia de teste — Dados para SQL"]];
guide.getRange("A4:B10").values = [
  ["Objetivo", "Testar identificação da aba, sanitização, relatório CSV e geração de SQL."],
  ["Cabeçalho", "A aba correta não é a primeira e o cabeçalho está na linha 4."],
  ["Nomes", "Inclui maiúsculas, minúsculas, aspas, apóstrofos no começo, meio e fim."],
  ["CPF", "Inclui formato, sem formato, válido, inválido e valor com 10 dígitos."],
  ["LGPD", "Apenas SIM permite geração de INSERT. NÃO e valores inválidos ficam no relatório."],
  ["Saída esperada", "valid_records.csv, errors.csv, summary.json e inserts.sql."],
  ["Privacidade", "Todos os dados são fictícios e usados exclusivamente para teste."],
];

summary.getRange("A1:C4").values = [
  ["Resumo de exemplo", null, null],
  ["Métrica", "Quantidade", "Observação"],
  ["Linhas", 10, "Não usar esta aba como fonte"],
  ["Válidas esperadas", 6, "As demais devem aparecer no relatório"],
];

customers.getRange("A1:F4").values = [
  ["CADASTRO FICTÍCIO PARA TESTES", null, null, null, null, null],
  ["Planilha propositalmente malformada", null, null, null, null, null],
  [null, null, null, null, null, null],
  [" NOME COMPLETO ", " C.P.F. ", "E-mail", "Telefone ", "Endereço", "Aceita LGPD (SIM, Não)"],
];

const rows = [
  [" ANA D'ÁVILA ", "529.982.247-25", " ANA.DAVILA@EXAMPLE.COM ", "(11) 99999-9999", " Rua São João, 10 ", "sim"],
  ['"Carlos "Cacá" O\'Neil"', "39053344705", "carlos.oneil@EXAMPLE.com", "+55 (21) 98888-7777", "Av. Brasil,   250", "SIM"],
  ["MARIA DAS DORES'", "168.995.350-09", "maria.dores@example.com", "11988887777", "Rua das Flores, 15", "S"],
  ["JOÃO DA SILVA", "111.111.111-11", "joao@@example.com", "123", "Rua A, 1", "Não"],
  ["'Maria Começo", "1234567890", "maria.comeco@example.com", "(31) 97777-6666", "Rua do Sol, 22", "SIM"],
  ['Ana "Juca" Souza', "11144477735", "ANA.JUCA@EXAMPLE.COM", "11 96666-5555", "  Travessa Azul,  9 ", "Sim"],
  ["O'CONNOR", "12345678909", "oconnor@example.com", "11995554444", "Rua O'Connor, 100", "SIM"],
  ["'Mariana Souza'", "93541134780", "mariana.souza@example.com", "(41) 98888-9999", "Rua das Acácias, 55", "SIM"],
  ["Paulo Sem LGPD", "52998224725", "paulo@example.com", "11992223333", "Rua Central, 1", "NÃO"],
  ["Lia Sem Endereço", "39053344705", "lia@example.com", "11991112222", "", "Talvez"],
];
customers.getRange("A5:F14").values = rows;

for (const sheet of [guide, summary, customers]) {
  sheet.showGridLines = false;
  const used = sheet.getUsedRange();
  used.format.font = { name: "Arial", size: 10, color: "#1F2937" };
  used.format.verticalAlignment = "center";
}

guide.getRange("A2:F2").format = {
  font: { name: "Arial", size: 14, bold: true, color: "#1F4E78" },
};
guide.getRange("A4:A10").format = {
  fill: "#D9EAF7",
  font: { name: "Arial", size: 10, bold: true, color: "#1F2937" },
};
guide.getRange("A4:B10").format.borders = { preset: "inside", style: "thin", color: "#D1D5DB" };
guide.getRange("A4:B10").format.wrapText = true;
guide.getRange("A4").format.columnWidth = 22;
guide.getRange("B4").format.columnWidth = 85;

summary.getRange("A1:C1").format = {
  fill: "#6B7280",
  font: { name: "Arial", size: 12, bold: true, color: "#FFFFFF" },
};
summary.getRange("A2:C2").format = {
  fill: "#D1D5DB",
  font: { name: "Arial", size: 10, bold: true, color: "#111827" },
};

customers.getRange("A1:F1").format = {
  font: { name: "Arial", size: 14, bold: true, color: "#1F4E78" },
};
customers.getRange("A4:F4").format = {
  fill: "#1F4E78",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
  wrapText: true,
};
customers.getRange("A5:F14").format.borders = {
  preset: "inside",
  style: "thin",
  color: "#E5E7EB",
};
customers.freezePanes.freezeRows(4);
customers.getRange("A:F").format.autofitColumns();
customers.getRange("A:A").format.columnWidth = 27;
customers.getRange("C:C").format.columnWidth = 32;
customers.getRange("E:E").format.columnWidth = 32;
customers.getRange("F:F").format.columnWidth = 25;

workbook.recalculate();
const inspection = await workbook.inspect({
  kind: "table",
  range: " Cadastro de Clientes !A1:F14",
  include: "values,formulas",
  tableMaxRows: 14,
  tableMaxCols: 6,
});
console.log(inspection.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);
const preview = await workbook.render({
  sheetName: " Cadastro de Clientes ",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(outputDir + "/cadastro_ficticio_preview.png", new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputDir + "/cadastro_ficticio_malformatado.xlsx");
