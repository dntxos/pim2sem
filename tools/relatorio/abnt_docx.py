"""Motor de formatação ABNT/UNIP para python-docx.

Regras (Guia de Normalização ABNT da Biblioteca UNIP, 2025 / NBR 14724:2024):
A4; margens 3 cm (esq./sup.) e 2 cm (dir./inf.); Times New Roman 12; entrelinhas 1,5; parágrafo
justificado com recuo de 1,25 cm; títulos de seção à esquerda (primária MAIÚSCULA negrito);
títulos sem número centralizados; legendas de ilustração em cima e fonte embaixo (tamanho 10);
paginação no canto superior direito a partir da Introdução, contando desde a folha de rosto.

Marcação inline aceita nos textos: **negrito**, *itálico*, `código` e [PREENCHER: ...] (realçado em amarelo).
"""
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

FONTE = 'Times New Roman'
ESTILO_FIG = 'Legenda Figura'
ESTILO_TAB = 'Legenda Tabela'


def _fonte(run_ou_estilo, tamanho=12, negrito=None, italico=None):
    f = run_ou_estilo.font
    f.name = FONTE
    f.size = Pt(tamanho)
    if negrito is not None:
        f.bold = negrito
    if italico is not None:
        f.italic = italico
    el = run_ou_estilo.element if hasattr(run_ou_estilo, 'element') else run_ou_estilo._element
    rpr = el.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rfonts.set(qn(a), FONTE)
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        if rfonts.get(qn(a)) is not None:
            del rfonts.attrib[qn(a)]


def _campo(paragrafo, instrucao, texto_previo=' '):
    """Insere um campo do Word (PAGE, TOC...)."""
    r = paragrafo.add_run()
    ini = OxmlElement('w:fldChar'); ini.set(qn('w:fldCharType'), 'begin')
    ins = OxmlElement('w:instrText'); ins.set(qn('xml:space'), 'preserve'); ins.text = instrucao
    sep = OxmlElement('w:fldChar'); sep.set(qn('w:fldCharType'), 'separate')
    r._r.append(ini); r._r.append(ins); r._r.append(sep)
    r2 = paragrafo.add_run(texto_previo)
    fim = OxmlElement('w:fldChar'); fim.set(qn('w:fldCharType'), 'end')
    r2._r.append(fim)
    return r


class Relatorio:
    def __init__(self):
        self.doc = Document()
        self.n_fig = 0
        self.n_tab = 0
        self.n_quadro = 0
        self.n_eq = 0
        self._configurar()

    # ------------------------------------------------------------ configuração
    def _configurar(self):
        d = self.doc
        s = d.sections[0]
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.left_margin, s.top_margin = Cm(3), Cm(3)
        s.right_margin, s.bottom_margin = Cm(2), Cm(2)
        s.header_distance = Cm(2)
        st = d.styles
        n = st['Normal']
        _fonte(n, 12)
        pf = n.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.first_line_indent = Cm(1.25)
        pf.widow_control = True
        for nivel, (negr, maius) in enumerate(((True, True), (True, False), (False, False)), start=1):
            h = st[f'Heading {nivel}']
            _fonte(h, 12, negrito=negr, italico=False)
            h.font.color.rgb = RGBColor(0, 0, 0)
            h.font.all_caps = maius
            p = h.paragraph_format
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.first_line_indent = Cm(0)
            p.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            p.space_before = Pt(18 if nivel > 1 else 0)
            p.space_after = Pt(18)
            p.keep_with_next = True
            p.page_break_before = nivel == 1
        for nome, tam, alin in ((ESTILO_FIG, 10, WD_ALIGN_PARAGRAPH.CENTER), (ESTILO_TAB, 10, WD_ALIGN_PARAGRAPH.LEFT),
                                ('Fonte ABNT', 10, WD_ALIGN_PARAGRAPH.LEFT), ('Codigo', 8.5, WD_ALIGN_PARAGRAPH.LEFT),
                                ('Citacao Longa', 10, WD_ALIGN_PARAGRAPH.JUSTIFY), ('Referencia', 12, WD_ALIGN_PARAGRAPH.LEFT),
                                ('Titulo Sem Numero', 12, WD_ALIGN_PARAGRAPH.CENTER)):
            e = st.add_style(nome, 1)
            e.base_style = n
            _fonte(e, tam)
            p = e.paragraph_format
            p.alignment = alin
            p.first_line_indent = Cm(0)
            p.line_spacing_rule = WD_LINE_SPACING.SINGLE
            p.space_after = Pt(0)
        st[ESTILO_FIG].paragraph_format.space_before = Pt(12)
        st[ESTILO_FIG].paragraph_format.space_after = Pt(4)
        st[ESTILO_FIG].paragraph_format.keep_with_next = True
        st[ESTILO_TAB].paragraph_format.space_before = Pt(12)
        st[ESTILO_TAB].paragraph_format.space_after = Pt(4)
        st[ESTILO_TAB].paragraph_format.keep_with_next = True
        st['Fonte ABNT'].paragraph_format.space_before = Pt(3)
        st['Fonte ABNT'].paragraph_format.space_after = Pt(12)
        st['Codigo'].font.name = 'Courier New'
        st['Codigo'].element.rPr.rFonts.set(qn('w:ascii'), 'Courier New')
        st['Codigo'].element.rPr.rFonts.set(qn('w:hAnsi'), 'Courier New')
        st['Citacao Longa'].paragraph_format.left_indent = Cm(4)
        st['Citacao Longa'].paragraph_format.space_before = Pt(12)
        st['Citacao Longa'].paragraph_format.space_after = Pt(12)
        st['Referencia'].paragraph_format.space_after = Pt(12)
        tsn = st['Titulo Sem Numero']
        tsn.font.bold = True
        tsn.font.all_caps = True
        tsn.paragraph_format.space_after = Pt(18)
        tsn.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        # atualizar campos (sumário, listas, páginas) ao abrir no Word
        upd = OxmlElement('w:updateFields'); upd.set(qn('w:val'), 'true')
        d.settings.element.append(upd)
        # idioma
        rpr = st['Normal'].element.get_or_add_rPr()
        lang = OxmlElement('w:lang'); lang.set(qn('w:val'), 'pt-BR')
        rpr.append(lang)

    # ------------------------------------------------------------ texto
    def _runs(self, p, texto, tamanho=None):
        partes = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[PREENCHER:[^\]]*\])', texto)
        for parte in partes:
            if not parte:
                continue
            if parte.startswith('**'):
                r = p.add_run(parte[2:-2]); r.bold = True
            elif parte.startswith('[PREENCHER'):
                r = p.add_run(parte); r.font.highlight_color = WD_COLOR_INDEX.YELLOW; r.bold = True
            elif parte.startswith('*'):
                r = p.add_run(parte[1:-1]); r.italic = True
            elif parte.startswith('`'):
                r = p.add_run(parte[1:-1]); r.font.name = 'Courier New'; r.font.size = Pt(10.5)
            else:
                r = p.add_run(parte)
            if tamanho:
                r.font.size = Pt(tamanho)
        return p

    def p(self, texto, estilo=None, alin=None, recuo=True, tamanho=None, antes=None, depois=None):
        par = self.doc.add_paragraph(style=estilo)
        if not recuo:
            par.paragraph_format.first_line_indent = Cm(0)
        if alin is not None:
            par.paragraph_format.alignment = alin
        if antes is not None:
            par.paragraph_format.space_before = Pt(antes)
        if depois is not None:
            par.paragraph_format.space_after = Pt(depois)
        return self._runs(par, texto, tamanho)

    def ps(self, *textos):
        for t in textos:
            self.p(t)

    def itens(self, itens, marcador='•', alin=WD_ALIGN_PARAGRAPH.JUSTIFY):
        for i, t in enumerate(itens):
            m = f'{chr(97 + i)})' if marcador == 'a' else marcador
            par = self.doc.add_paragraph()
            pf = par.paragraph_format
            pf.first_line_indent = Cm(-0.6)
            pf.left_indent = Cm(1.85)
            pf.alignment = alin
            self._runs(par, f'{m} {t}')

    def h1(self, t):
        return self.doc.add_heading(t, 1)

    def h2(self, t):
        return self.doc.add_heading(t, 2)

    def h3(self, t):
        return self.doc.add_heading(t, 3)

    def titulo_sem_numero(self, t, quebra=True):
        par = self.doc.add_paragraph(t, style='Titulo Sem Numero')
        par.paragraph_format.page_break_before = quebra
        return par

    def quebra(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def espaco(self, n=1):
        for _ in range(n):
            self.doc.add_paragraph()

    # ------------------------------------------------------------ ilustrações
    def _legenda(self, estilo, rotulo, numero, titulo):
        cap = self.doc.add_paragraph(style=estilo)
        cap.add_run(f'{rotulo} ').font.size = Pt(10)
        _campo(cap, f'SEQ {rotulo} \\* ARABIC', str(numero))
        for run in cap.runs:
            run.font.size = Pt(10)
        self._runs(cap, f' – {titulo}', 10)
        return cap

    def figura(self, caminho, titulo, fonte='Autoria própria, 2026.', largura=15.5, tipo='Figura'):
        self.n_fig += 1
        self._legenda(ESTILO_FIG, 'Figura', self.n_fig, titulo)
        img = self.doc.add_paragraph()
        img.paragraph_format.first_line_indent = Cm(0)
        img.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        img.paragraph_format.keep_with_next = True
        img.add_run().add_picture(caminho, width=Cm(largura))
        f = self.doc.add_paragraph(style='Fonte ABNT')
        f.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._runs(f, f'Fonte: {fonte}', 10)
        return self.n_fig

    def prox_fig(self, k=1):
        return self.n_fig + k

    def prox_tab(self, quadro=False, k=1):
        return (self.n_quadro if quadro else self.n_tab) + k

    def tabela(self, titulo, cab, linhas, fonte='Autoria própria, 2026.', larguras=None, quadro=False, tam=10):
        if quadro:
            self.n_quadro += 1
            self._legenda(ESTILO_TAB, 'Quadro', self.n_quadro, titulo)
        else:
            self.n_tab += 1
            self._legenda(ESTILO_TAB, 'Tabela', self.n_tab, titulo)
        t = self.doc.add_table(rows=1, cols=len(cab))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        self._bordas(t, quadro)
        for i, c in enumerate(cab):
            cel = t.rows[0].cells[i]
            cel.text = ''
            par = cel.paragraphs[0]
            self._fmt_cel(par)
            self._runs(par, f'**{c}**', tam)
            self._sombrear(cel, 'E5E7EB')
        self._repetir_cabecalho(t.rows[0])
        for linha in linhas:
            cells = t.add_row().cells
            for i, v in enumerate(linha):
                cells[i].text = ''
                par = cells[i].paragraphs[0]
                self._fmt_cel(par)
                self._runs(par, str(v), tam)
        if larguras:
            for row in t.rows:
                for i, w in enumerate(larguras):
                    row.cells[i].width = Cm(w)
        f = self.doc.add_paragraph(style='Fonte ABNT')
        self._runs(f, f'Fonte: {fonte}', 10)
        return t

    def _fmt_cel(self, par):
        pf = par.paragraph_format
        pf.first_line_indent = Cm(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.space_before = Pt(2)
        pf.space_after = Pt(2)

    @staticmethod
    def _sombrear(cel, cor):
        tcpr = cel._tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), cor)
        tcpr.append(shd)

    @staticmethod
    def _repetir_cabecalho(row):
        trpr = row._tr.get_or_add_trPr()
        h = OxmlElement('w:tblHeader'); h.set(qn('w:val'), 'true')
        trpr.append(h)

    @staticmethod
    def _bordas(tabela, quadro):
        tblpr = tabela._tbl.tblPr
        b = OxmlElement('w:tblBorders')
        lados = ('top', 'left', 'bottom', 'right', 'insideH', 'insideV') if quadro else ('top', 'bottom', 'insideH')
        for lado in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            e = OxmlElement(f'w:{lado}')
            if lado in lados:
                e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '6'); e.set(qn('w:color'), '000000')
            else:
                e.set(qn('w:val'), 'nil')
            b.append(e)
        tblpr.append(b)

    def equacao(self, expr, onde=None):
        self.n_eq += 1
        par = self.doc.add_paragraph()
        pf = par.paragraph_format
        pf.first_line_indent = Cm(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.space_before = Pt(6)
        pf.space_after = Pt(6)
        pf.tab_stops.add_tab_stop(Cm(8), WD_TAB_ALIGNMENT.CENTER)
        pf.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT)
        r = par.add_run(f'\t{expr}\t({self.n_eq})'); r.italic = False
        if onde:
            self.p(onde, recuo=False)
        return self.n_eq

    def codigo(self, texto, titulo=None, fonte='Autoria própria, 2026 (trecho de `main.c`).'):
        if titulo:
            self.n_quadro += 1
            self._legenda(ESTILO_TAB, 'Quadro', self.n_quadro, titulo)
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        self._bordas(t, True)
        cel = t.rows[0].cells[0]
        self._sombrear(cel, 'F3F4F6')
        cel.text = ''
        linhas = texto.strip('\n').split('\n')
        for i, l in enumerate(linhas):
            par = cel.paragraphs[0] if i == 0 else cel.add_paragraph()
            par.style = self.doc.styles['Codigo']
            r = par.add_run(l if l else ' ')
            r.font.name = 'Courier New'
            r.font.size = Pt(8.5)
        if titulo:
            f = self.doc.add_paragraph(style='Fonte ABNT')
            self._runs(f, f'Fonte: {fonte}', 10)
        else:
            self.espaco()

    def citacao_longa(self, texto):
        self.p(texto, estilo='Citacao Longa', recuo=False)

    # ------------------------------------------------------------ sumário e listas
    def sumario(self):
        self.titulo_sem_numero('SUMÁRIO')
        par = self.doc.add_paragraph()
        par.paragraph_format.first_line_indent = Cm(0)
        _campo(par, 'TOC \\o "1-3" \\h \\z \\u', 'Clique com o botão direito e escolha "Atualizar campo" para gerar o sumário.')

    def listas(self, titulo, rotulos):
        """Uma página com várias listas (ex.: tabelas e quadros), uma por rótulo."""
        self.titulo_sem_numero(titulo)
        for rotulo in rotulos:
            par = self.doc.add_paragraph()
            par.paragraph_format.first_line_indent = Cm(0)
            par.paragraph_format.space_after = Pt(6)
            _campo(par, f'TOC \\h \\z \\c "{rotulo}"', 'Atualize o campo para gerar a lista.')

    def lista(self, titulo, rotulo):
        """Lista de ilustrações/tabelas/quadros a partir dos campos SEQ das legendas."""
        self.titulo_sem_numero(titulo)
        par = self.doc.add_paragraph()
        par.paragraph_format.first_line_indent = Cm(0)
        _campo(par, f'TOC \\h \\z \\c "{rotulo}"', 'Atualize o campo para gerar a lista.')

    # ------------------------------------------------------------ seções e paginação
    def iniciar_texto(self):
        """Nova seção a partir da Introdução: numeração visível no canto superior direito."""
        nova = self.doc.add_section(WD_SECTION.NEW_PAGE)
        nova.header.is_linked_to_previous = False
        par = nova.header.paragraphs[0]
        par.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        par.paragraph_format.first_line_indent = Cm(0)
        r = _campo(par, 'PAGE', '1')
        for run in par.runs:
            run.font.size = Pt(10)
            run.font.name = FONTE
        # 1ª seção: sem número; começa em 0 para que a folha de rosto seja a página 1
        primeira = self.doc.sections[0]
        primeira.header.is_linked_to_previous = False
        pg = OxmlElement('w:pgNumType'); pg.set(qn('w:start'), '0')
        primeira._sectPr.append(pg)
        return nova

    def salvar(self, caminho):
        self.doc.save(caminho)
