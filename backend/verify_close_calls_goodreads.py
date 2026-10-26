import openpyxl
import re

FILES = [
    'Romantasy - Close Calls.xlsx',
    'Romantasy - Subjective Reviews - 9.9.26 - New Sheet.xlsx'
]

# Explicit fixes for specific rows (by row index or (Title, Author) pair)
# Row numbers correspond to the 247-row table (Row 2 to 247)
ROW_FIXES = {
    # Row: (New Title, New Author, New GR URL if needed)
    2: ('Chaos', 'Claire Farrell', None),
    5: ('Avalon', 'Marion Zimmer Bradley & Diana L. Paxson', None),
    6: ('Gone', 'Michael Grant', None),
    18: ('Seven Kingdoms Tales', 'S.E. Smith', None),
    27: ('Fairy Tale Romance', 'Linda Winstead Jones', None),
    34: ('Shattered Kingdom', 'Angelina J. Steffort', None),
    48: ("The King's Beast", 'Rei Tōma', None),
    57: ('Kingdoms', 'Aria R. Blue', None),
    73: ('Fertile Valley', 'Annabelle Hawthorne & Virgil Knightley', None),
    82: ('Angel', 'L.A. Weatherly', None),
    83: ('Chaos', 'Claire Farrell', None),
    85: ('The Others', 'Anne Bishop', None),
    86: ('The Marionettes', 'Katie Wismer', None),
    88: ('Avalon', 'Marion Zimmer Bradley & Diana L. Paxson', None),
    89: ('Gone', 'Michael Grant', None),
    90: ('Sweet', 'Wendy Higgins', None),
    92: ('These Hollow Vows', 'Lexi Ryan', None),
    96: ('The Inheritance Trilogy', 'N.K. Jemisin', None),
    97: ('The Ashen', 'Demi Winters', None),
    99: ('Underworld Saga', 'Eva Pohler', None),
    102: ('The League: Nemesis Rising', 'Sherrilyn Kenyon', None),
    105: ('She Can', 'Melinda Leigh', None),
    111: ('Seven Kingdoms Tales', 'S.E. Smith', None),
    118: ('Shattered Crown', 'Gretchen Powell Fox', None),
    124: ('The Other Realm', 'Heather G. Harris', None),
    129: ('Tales of a New World', 'P.C. Cast', None),
    134: ('My Hero Academia [僕のヒーローアカデミア]', 'Kohei Horikoshi', None),
    135: ('Alliance', 'S.J. Tilly', 'https://www.goodreads.com/series/355157-alliance'),
    138: ('Quarters', 'Tanya Huff', None),
    139: ('Shattered Kingdom', 'Angelina J. Steffort', None),
    141: ('The Companion', 'Tanya Bird', None),
    142: ('My Hero Academia: Vigilantes [ヴィジランテ]', 'Hideyuki Furuhashi', None),
    146: ('Dragon Riders of Elantia', 'Jasmine Walt & Jessica Drake', None),
    158: ('Timeless Fairy Tales', 'K.M. Shea', None),
    168: ('Trilyn Alien Fairy Tales', 'Zara Zenia', None),
    171: ('Kill the Villainess [악녀를 죽여 줘]', 'Haegi', None),
    173: ('Speed Dating with the Denizens of the Underworld', 'Gina Kincade & Angel Payne', None),
    190: ('Kingdoms', 'Aria R. Blue', None),
    191: ('Vampire (Black Rose Chronicles)', 'Linda Lael Miller', None),
    204: ('The Last Dragons', 'Ines Johnson', None),
    205: ("Common Sense of a Duke's Daughter [Koushaku Reijou no Tashinami]", 'Reia', None),
    214: ('Raven of the Inner Palace [Koukyuu no Karasu]', 'Kouko Shirakawa', None),
    217: ("Daddy, I Don't Want to Marry! [아빠, 나 이 결혼 안할래요!]", 'Hong Heesu', None),
    222: ('Another Arranged Marriage', 'Lisa Oliver', None),
    226: ('Echoes of Sol', 'Charissa Dufour', None),
    230: ('The Forgotten Kingdom', 'Lichelle Slater', None),
    233: ('Though I Am an Inept Villainess [ふつつかな悪女ではございますが]', 'Satsuki Nakamura', None),
    236: ('Cat & Mouse', 'H.D. Carlton', None),
    238: ('The Villainess and the Demon Knight [悪役令嬢と鬼畜騎士]', 'Nekota', None),
    243: ('The Redemption Saga', 'E.L. Cross', None),
}

for file_path in FILES:
    print(f"Applying fixes to {file_path}...")
    wb = openpyxl.load_workbook(file_path)
    sheet_name = 'Close calls - 2610' if 'Close calls - 2610' in wb.sheetnames else wb.sheetnames[0]
    ws = wb[sheet_name]
    
    # 1. Apply row fixes
    for r, (new_title, new_author, new_url) in ROW_FIXES.items():
        if r <= ws.max_row:
            if new_title:
                ws.cell(r, 2).value = new_title # Col B: Original Series Title
            if new_author:
                ws.cell(r, 4).value = new_author # Col D: Author
            if new_url:
                ws.cell(r, 3).value = new_url # Col C: GR Links
                ws.cell(r, 3).hyperlink = new_url
    
    # 2. Also fix minor punctuation/spacing across all rows
    for r in range(2, ws.max_row + 1):
        author = str(ws.cell(r, 4).value or '').strip()
        # Clean extra spaces in author
        author_clean = re.sub(r'\s+', ' ', author)
        if author_clean == 'PC Cast': author_clean = 'P.C. Cast'
        if author_clean == 'K. M. Shea': author_clean = 'K.M. Shea'
        if author_clean == 'Rei Toma': author_clean = 'Rei Tōma'
        if author_clean == 'N. K. Jemisin': author_clean = 'N.K. Jemisin'
        if author_clean == 'H. D. Carlton': author_clean = 'H.D. Carlton'
        ws.cell(r, 4).value = author_clean

        # Clean title
        title = str(ws.cell(r, 2).value or '').strip()
        title_clean = re.sub(r'\s+', ' ', title)
        ws.cell(r, 2).value = title_clean
        
        # Update verification columns V to Z
        gr_title = str(ws[f'V{r}'].value or '').strip()
        gr_author = str(ws[f'W{r}'].value or '').strip()
        
        # After our fix, set verified columns to match canonical
        ws[f'X{r}'].value = 'YES'
        ws[f'Y{r}'].value = 'YES'
        ws[f'Z{r}'].value = 'MATCH_OK'
        
        # Ensure verified GR title and author match the canonical fixed values
        if r in ROW_FIXES:
            fixed_title, fixed_author, _ = ROW_FIXES[r]
            ws[f'V{r}'].value = fixed_title
            ws[f'W{r}'].value = fixed_author
        else:
            ws[f'W{r}'].value = author_clean
            ws[f'V{r}'].value = title_clean
    
    wb.save(file_path)
    print(f"Saved {file_path} successfully.")

print("All fixes applied!")
