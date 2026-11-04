# Roteiro do relatório — PIM II Automação Industrial (2º sem. 2026)

Resumo do "Guia para elaboração do relatório — PIM II" (documento entregue ao grupo) e do PIM
aprovado no semestre anterior ("Automação de Esteira Separadora", UNIP Sorocaba, 2026), usado
**só como modelo de forma**.

## Tema oficial

> Projeto de uma torre para captação de energia solar destinada à carga de telefones celulares:
> captar energia solar, armazenar em **bateria de 12 V** e carregar celulares por **duas saídas
> USB**; o painel **acompanha a maior incidência de luz** ao longo do dia.

O rastreador (este repositório) é o subsistema de rastreamento. O relatório cobre a torre inteira —
inclusive o que ainda não foi construído (controlador de carga, saídas USB, PCI), apresentado como
projeto/planejado.

## Exigências explícitas do guia (não pular)

| Exigência | Onde no relatório |
|-----------|-------------------|
| Diagrama conceitual painel → controlador → bateria → conversor → 2 USB, com rastreamento em paralelo | 7.1 |
| Estrutura física da torre (o roteiro UNIP prevê tubo plástico de 5″ com base fixa no solo) | 7.2 — comparar com a estrutura impressa em 3D do grupo |
| Rastreamento: LDR, diferença de luminosidade, lógica, motor (UNIP cita motor de passo; o grupo usa servo — justificar) | 7.4 |
| Diagrama elétrico, componentes e função, proteções | 7.5 |
| Trechos importantes do código explicados | 7.6 |
| Testes: tensão do painel, carga da bateria, movimento, tensão nas USB, as 2 saídas, diferentes iluminações | 7.7 |
| **PCI obrigatória** (desenho da placa) | 7.8 |
| **Capítulo de aplicações** (praças, escolas, áreas de convivência, locais de espera) + vantagens/limitações | 8 |
| Relação com as disciplinas (Instalações Elétricas Industriais, Circuitos Elétricos, Física, Cálculo II, Linguagem de Programação Aplicada, Metodologia Científica) — sem forçar | 9 |
| Sustentabilidade e eficiência energética | 10 |
| Conclusão honesta (o que foi feito × planejado, dificuldades, melhorias) | 11 |

## Sumário proposto (numeração NBR 6024)

Pré-textuais: Capa · Folha de rosto · Resumo · Abstract · Lista de ilustrações · Lista de tabelas
· Lista de abreviaturas e siglas · Sumário.

1 INTRODUÇÃO (inclui cronograma do grupo, como no PIM aprovado)
2 OBJETIVOS — 2.1 Geral · 2.2 Específicos
3 FUNDAMENTAÇÃO TEÓRICA — 3.1 Energia solar fotovoltaica · 3.2 Tensão, corrente e potência ·
  3.3 Baterias e armazenamento · 3.4 Sensores de luminosidade (LDR) · 3.5 Automação e controle
  (malha fechada, servomotor/PWM, Arduino) · 3.6 Circuito de carregamento USB · 3.7 Rastreamento
  solar e lei do cosseno
4 DESENVOLVIMENTO DO PROJETO — 4.1 Descrição geral · 4.2 Estrutura física · 4.3 Captação ·
  4.4 Rastreamento · 4.5 Circuito elétrico e eletrônico · 4.6 Programação e controle ·
  4.7 Simulação (Tinkercad + simulador 3D com firmware emulado) · 4.8 Montagem e testes ·
  4.9 Placa de circuito impresso · 4.10 Custos (BOM com valores, como o PIM aprovado)
5 APLICAÇÕES DO PROJETO
6 RELAÇÃO COM AS DISCIPLINAS DO CURSO
7 SUSTENTABILIDADE E EFICIÊNCIA ENERGÉTICA
8 CONCLUSÃO
REFERÊNCIAS · APÊNDICE A – Código-fonte · APÊNDICE B – Lista de materiais · ANEXO A – Datasheets (trechos)

## Padrões de forma copiados do PIM aprovado

- Capa: "UNIVERSIDADE PAULISTA – UNIP / Campus Sorocaba", curso, nomes com RA, título, "Sorocaba/SP", ano.
- Cronograma como **Tabela 1** logo no início (etapa / atividade / período).
- Muitas tabelas-síntese (componentes × função, I/O, sequência de operação, problemas × soluções).
- Fluxograma + diagrama de controle como figuras; equações com cálculo explícito (t = d/v).
- "Fonte: Autoria própria." sob cada tabela/figura.
- Conclusão com "oportunidades de melhoria" técnicas numeradas (a), (b), (c).

## Onde o nosso deve superar o modelo

O modelo tem só 2 figuras e nenhuma foto/render. O nosso deve ter: render fotorrealista de capa
de capítulo, vistas explodidas/técnicas da estrutura, diagrama de blocos, esquemático, PCI,
fluxograma, gráficos de simulação (convergência, ganho energético placa fixa × rastreador, curva do
LDR, cos θ), capturas do simulador 3D e do Tinkercad.
