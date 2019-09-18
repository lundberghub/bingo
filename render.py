from reportlab.lib import colors, enums
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, KeepTogether, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from copy import deepcopy


def create_bingo_cards_pdf(title, song_distribution, matrices, filename):
    print 'Creating "{}" bingo cards in {}'.format(title, filename)

    document = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.0, BottomMargin=0.0)
    stylesheet = getSampleStyleSheet()

    flowables = create_song_distribution_section(stylesheet, title, song_distribution) + \
                create_bingo_card_section(stylesheet, title, matrices)

    document.build(flowables)


def create_song_distribution_section(stylesheet, title, song_distribution):
    flowables = []

    if song_distribution:
        title_style = deepcopy(stylesheet['Title'])
        cell_style = deepcopy(stylesheet['Normal'])
        cell_style.alignment = enums.TA_LEFT
        cell_style.leading = 4
        cell_style.fontSize = 7

        data = [[Paragraph(song[0], cell_style), Paragraph(song[1], cell_style), Paragraph(str(song[2]), cell_style)]
                for song in song_distribution]
        table = Table(data, colWidths=[3*inch, 3*inch, 1*inch], normalizedData=True)

        flowables.append(KeepTogether([
            Spacer(1, 0.1*inch),
            Paragraph('"{}" Bingo Card Song Distribution'.format(title), title_style),
            Spacer(1, 0.1*inch),
            table
        ]))

    return flowables


def create_bingo_card_section(stylesheet, title, matrices):
    title_style = deepcopy(stylesheet['Title'])
    cell_style = deepcopy(stylesheet['Normal'])
    cell_style.alignment = enums.TA_CENTER
    cell_style.leading = 10

    table_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1.0, colors.black),
        ('BOX',       (0, 0), (-1, -1), 1.2, colors.black),
        ('FONTSIZE',  (0, 0), (-1, -1), 10),
        ('VALIGN',    (0, 0), (-1, -1), 'MIDDLE')
    ])

    flowables = []

    # emit title and song matrix for each bingo card
    for matrix in matrices:
        assert matrix, len(matrix) == len(matrix[0])
        size = len(matrix)
        data = [[BingoCardCell(matrix[y][x].title, cell_style) for x in range(size)] for y in range(size)]
        # data = [[Paragraph(matrix[y][x].title, cell_style) for x in range(size)] for y in range(size)]
        table = Table(data, size*[0.8*inch], size*[0.8*inch], table_style, 0, 1, None, None, None, None, 1, None)
        flowables.append(KeepTogether([
            Spacer(1, 0.5*inch),
            Paragraph(title, title_style),
            table
        ]))

    return flowables


class BingoCardCell(Paragraph):

    def __init__(self, text, style, bulletText = None, frags=None, caseSensitive=1, encoding='utf8'):
        Paragraph.__init__(self, text, style, bulletText, frags, caseSensitive, encoding)

    def wrap(self, availWidth, availHeight):
        # select font size according to cell text length
        text_length = sum([len(frag.text) for frag in self.frags])
        for frag in self.frags:
            for text_limit, font_size in [(0, 10), (20, 9), (25, 8), (30, 7), (40, 6)]:
                if text_length > text_limit:
                    # print '{} len({}) fontsize {} -> {}'.format(frag.text, text_length, frag.fontSize, font_size)
                    frag.fontSize = font_size

        return Paragraph.wrap(self, availWidth, availHeight)


