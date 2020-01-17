import os
import sys
from random import randint, random

from django.core.wsgi import get_wsgi_application
proj_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "washer_project.settings")
sys.path.append(proj_path)
os.chdir(proj_path)
application = get_wsgi_application()


"""********************************************************************"""
"""******************** ADDRESS MIGRATION *****************************"""
"""********************************************************************"""
cities = {'1': 'ADANA', '2': 'ADIYAMAN', '3': 'AFYONKARAHİSAR', '4': 'AĞRI', '5': 'AMASYA', '6': 'ANKARA', '7': 'ANTALYA', '8': 'ARTVİN', '9': 'AYDIN', '10': 'BALIKESİR', '11': 'BİLECİK', '12': 'BİNGÖL', '13': 'BİTLİS', '14': 'BOLU', '15': 'BURDUR', '16': 'BURSA', '17': 'ÇANAKKALE', '18': 'ÇANKIRI', '19': 'ÇORUM', '20': 'DENİZLİ', '21': 'DİYARBAKIR', '22': 'EDİRNE', '23': 'ELAZIĞ', '24': 'ERZİNCAN', '25': 'ERZURUM', '26': 'ESKİŞEHİR', '27': 'GAZİANTEP', '28': 'GİRESUN', '29': 'GÜMÜŞHANE', '30': 'HAKKARİ', '31': 'HATAY', '32': 'ISPARTA', '33': 'MERSİN', '34': 'İSTANBUL', '35': 'İZMİR', '36': 'KARS', '37': 'KASTAMONU', '38': 'KAYSERİ', '39': 'KIRKLARELİ', '40': 'KIRŞEHİR', '41': 'KOCAELİ', '42': 'KONYA', '43': 'KÜTAHYA', '44': 'MALATYA', '45': 'MANİSA', '46': 'KAHRAMANMARAŞ', '47': 'MARDİN', '48': 'MUĞLA', '49': 'MUŞ', '50': 'NEVŞEHİR', '51': 'NİĞDE', '52': 'ORDU', '53': 'RİZE', '54': 'SAKARYA', '55': 'SAMSUN', '56': 'SİİRT', '57': 'SİNOP', '58': 'SİVAS', '59': 'TEKİRDAĞ', '60': 'TOKAT', '61': 'TRABZON', '62': 'TUNCELİ', '63': 'ŞANLIURFA', '64': 'UŞAK', '65': 'VAN', '66': 'YOZGAT', '67': 'ZONGULDAK', '68': 'AKSARAY', '69': 'BAYBURT', '70': 'KARAMAN', '71': 'KIRIKKALE', '72': 'BATMAN', '73': 'ŞIRNAK', '74': 'BARTIN', '75': 'ARDAHAN', '76': 'IĞDIR', '77': 'YALOVA', '78': 'KARABÜK', '79': 'KİLİS', '80': 'OSMANİYE', '81': 'DÜZCE'}
townships = {'1': ['ALADAĞ', 'CEYHAN', 'ÇUKUROVA', 'FEKE', 'İMAMOĞLU', 'KARAİSALI', 'KARATAŞ', 'KOZAN', 'POZANTI', 'SAİMBEYLİ', 'SARIÇAM', 'SEYHAN', 'TUFANBEYLİ', 'YUMURTALIK', 'YÜREĞİR'], '2': ['BESNİ', 'ÇELİKHAN', 'GERGER', 'GÖLBAŞI', 'KAHTA', 'MERKEZ', 'SAMSAT', 'SİNCİK', 'TUT'], '3': ['BAŞMAKÇI', 'BAYAT', 'BOLVADİN', 'ÇAY', 'ÇOBANLAR', 'DAZKIRI', 'DİNAR', 'EMİRDAĞ', 'EVCİLER', 'HOCALAR', 'İHSANİYE', 'İSCEHİSAR', 'KIZILÖREN', 'MERKEZ', 'SANDIKLI', 'SİNANPAŞA', 'SULTANDAĞI', 'ŞUHUT'], '4': ['DİYADİN', 'DOĞUBAYAZIT', 'ELEŞKİRT', 'HAMUR', 'MERKEZ', 'PATNOS', 'TAŞLIÇAY', 'TUTAK'], '5': ['GÖYNÜCEK', 'GÜMÜŞHACIKÖY', 'HAMAMÖZÜ', 'MERKEZ', 'MERZİFON', 'SULUOVA', 'TAŞOVA'], '6': ['AKYURT', 'ALTINDAĞ', 'AYAŞ', 'BALA', 'BEYPAZARI', 'ÇAMLIDERE', 'ÇANKAYA', 'ÇUBUK', 'ELMADAĞ', 'ETİMESGUT', 'EVREN', 'GÖLBAŞI', 'GÜDÜL', 'HAYMANA', 'KAHRAMANKAZAN', 'KALECİK', 'KEÇİÖREN', 'KIZILCAHAMAM', 'MAMAK', 'NALLIHAN', 'POLATLI', 'PURSAKLAR', 'SİNCAN', 'ŞEREFLİKOÇHİSAR', 'YENİMAHALLE'], '7': ['AKSEKİ', 'AKSU', 'ALANYA', 'DEMRE', 'DÖŞEMEALTI', 'ELMALI', 'FİNİKE', 'GAZİPAŞA', 'GÜNDOĞMUŞ', 'İBRADI', 'KAŞ', 'KEMER', 'KEPEZ', 'KONYAALTI', 'KORKUTELİ', 'KUMLUCA', 'MANAVGAT', 'MURATPAŞA', 'SERİK'], '8': ['ARDANUÇ', 'ARHAVİ', 'BORÇKA', 'HOPA', 'MERKEZ', 'MURGUL', 'ŞAVŞAT', 'YUSUFELİ'], '9': ['BOZDOĞAN', 'BUHARKENT', 'ÇİNE', 'DİDİM', 'EFELER', 'GERMENCİK', 'İNCİRLİOVA', 'KARACASU', 'KARPUZLU', 'KOÇARLI', 'KÖŞK', 'KUŞADASI', 'KUYUCAK', 'NAZİLLİ', 'SÖKE', 'SULTANHİSAR', 'YENİPAZAR'], '10': ['ALTIEYLÜL', 'AYVALIK', 'BALYA', 'BANDIRMA', 'BİGADİÇ', 'BURHANİYE', 'DURSUNBEY', 'EDREMİT', 'ERDEK', 'GÖMEÇ', 'GÖNEN', 'HAVRAN', 'İVRİNDİ', 'KARESİ', 'KEPSUT', 'MANYAS', 'MARMARA', 'SAVAŞTEPE', 'SINDIRGI', 'SUSURLUK'], '11': ['BOZÜYÜK', 'GÖLPAZARI', 'İNHİSAR', 'MERKEZ', 'OSMANELİ', 'PAZARYERİ', 'SÖĞÜT', 'YENİPAZAR'], '12': ['ADAKLI', 'GENÇ', 'KARLIOVA', 'KİĞI', 'MERKEZ', 'SOLHAN', 'YAYLADERE', 'YEDİSU'], '13': ['ADİLCEVAZ', 'AHLAT', 'GÜROYMAK', 'HİZAN', 'MERKEZ', 'MUTKİ', 'TATVAN'], '14': ['DÖRTDİVAN', 'GEREDE', 'GÖYNÜK', 'KIBRISCIK', 'MENGEN', 'MERKEZ', 'MUDURNU', 'SEBEN', 'YENİÇAĞA'], '15': ['AĞLASUN', 'ALTINYAYLA', 'BUCAK', 'ÇAVDIR', 'ÇELTİKÇİ', 'GÖLHİSAR', 'KARAMANLI', 'KEMER', 'MERKEZ', 'TEFENNİ', 'YEŞİLOVA'], '16': ['BÜYÜKORHAN', 'GEMLİK', 'GÜRSU', 'HARMANCIK', 'İNEGÖL', 'İZNİK', 'KARACABEY', 'KELES', 'KESTEL', 'MUDANYA', 'MUSTAFAKEMALPAŞA', 'NİLÜFER', 'ORHANELİ', 'ORHANGAZİ', 'OSMANGAZİ', 'YENİŞEHİR', 'YILDIRIM'], '17': ['AYVACIK', 'BAYRAMİÇ', 'BİGA', 'BOZCAADA', 'ÇAN', 'ECEABAT', 'EZİNE', 'GELİBOLU', 'GÖKÇEADA', 'LAPSEKİ', 'MERKEZ', 'YENİCE'], '18': ['ATKARACALAR', 'BAYRAMÖREN', 'ÇERKEŞ', 'ELDİVAN', 'ILGAZ', 'KIZILIRMAK', 'KORGUN', 'KURŞUNLU', 'MERKEZ', 'ORTA', 'ŞABANÖZÜ', 'YAPRAKLI'], '19': ['ALACA', 'BAYAT', 'BOĞAZKALE', 'DODURGA', 'İSKİLİP', 'KARGI', 'LAÇİN', 'MECİTÖZÜ', 'MERKEZ', 'OĞUZLAR', 'ORTAKÖY', 'OSMANCIK', 'SUNGURLU', 'UĞURLUDAĞ'], '20': ['ACIPAYAM', 'BABADAĞ', 'BAKLAN', 'BEKİLLİ', 'BEYAĞAÇ', 'BOZKURT', 'BULDAN', 'ÇAL', 'ÇAMELİ', 'ÇARDAK', 'ÇİVRİL', 'GÜNEY', 'HONAZ', 'KALE', 'MERKEZEFENDİ', 'PAMUKKALE', 'SARAYKÖY', 'SERİNHİSAR', 'TAVAS'], '21': ['BAĞLAR', 'BİSMİL', 'ÇERMİK', 'ÇINAR', 'ÇÜNGÜŞ', 'DİCLE', 'EĞİL', 'ERGANİ', 'HANİ', 'HAZRO', 'KAYAPINAR', 'KOCAKÖY', 'KULP', 'LİCE', 'SİLVAN', 'SUR', 'YENİŞEHİR'], '22': ['ENEZ', 'HAVSA', 'İPSALA', 'KEŞAN', 'LALAPAŞA', 'MERİÇ', 'MERKEZ', 'SÜLOĞLU', 'UZUNKÖPRÜ'], '23': ['AĞIN', 'ALACAKAYA', 'ARICAK', 'BASKİL', 'KARAKOÇAN', 'KEBAN', 'KOVANCILAR', 'MADEN', 'MERKEZ', 'PALU', 'SİVRİCE'], '24': ['ÇAYIRLI', 'İLİÇ', 'KEMAH', 'KEMALİYE', 'MERKEZ', 'OTLUKBELİ', 'REFAHİYE', 'TERCAN', 'ÜZÜMLÜ'], '25': ['AŞKALE', 'AZİZİYE', 'ÇAT', 'HINIS', 'HORASAN', 'İSPİR', 'KARAÇOBAN', 'KARAYAZI', 'KÖPRÜKÖY', 'NARMAN', 'OLTU', 'OLUR', 'PALANDÖKEN', 'PASİNLER', 'PAZARYOLU', 'ŞENKAYA', 'TEKMAN', 'TORTUM', 'UZUNDERE', 'YAKUTİYE'], '26': ['ALPU', 'BEYLİKOVA', 'ÇİFTELER', 'GÜNYÜZÜ', 'HAN', 'İNÖNÜ', 'MAHMUDİYE', 'MİHALGAZİ', 'MİHALIÇÇIK', 'ODUNPAZARI', 'SARICAKAYA', 'SEYİTGAZİ', 'SİVRİHİSAR', 'TEPEBAŞI'], '27': ['ARABAN', 'İSLAHİYE', 'KARKAMIŞ', 'NİZİP', 'NURDAĞI', 'OĞUZELİ', 'ŞAHİNBEY', 'ŞEHİTKAMİL', 'YAVUZELİ'], '28': ['ALUCRA', 'BULANCAK', 'ÇAMOLUK', 'ÇANAKÇI', 'DERELİ', 'DOĞANKENT', 'ESPİYE', 'EYNESİL', 'GÖRELE', 'GÜCE', 'KEŞAP', 'MERKEZ', 'PİRAZİZ', 'ŞEBİNKARAHİSAR', 'TİREBOLU', 'YAĞLIDERE'], '29': ['KELKİT', 'KÖSE', 'KÜRTÜN', 'MERKEZ', 'ŞİRAN', 'TORUL'], '30': ['ÇUKURCA', 'MERKEZ', 'ŞEMDİNLİ', 'YÜKSEKOVA'], '31': ['ALTINÖZÜ', 'ANTAKYA', 'ARSUZ', 'BELEN', 'DEFNE', 'DÖRTYOL', 'ERZİN', 'HASSA', 'İSKENDERUN', 'KIRIKHAN', 'KUMLU', 'PAYAS', 'REYHANLI', 'SAMANDAĞ', 'YAYLADAĞI'], '32': ['AKSU', 'ATABEY', 'EĞİRDİR', 'GELENDOST', 'GÖNEN', 'KEÇİBORLU', 'MERKEZ', 'SENİRKENT', 'SÜTÇÜLER', 'ŞARKİKARAAĞAÇ', 'ULUBORLU', 'YALVAÇ', 'YENİŞARBADEMLİ'], '33': ['AKDENİZ', 'ANAMUR', 'AYDINCIK', 'BOZYAZI', 'ÇAMLIYAYLA', 'ERDEMLİ', 'GÜLNAR', 'MEZİTLİ', 'MUT', 'SİLİFKE', 'TARSUS', 'TOROSLAR', 'YENİŞEHİR'], '34': ['ADALAR', 'ARNAVUTKÖY', 'ATAŞEHİR', 'AVCILAR', 'BAĞCILAR', 'BAHÇELİEVLER', 'BAKIRKÖY', 'BAŞAKŞEHİR', 'BAYRAMPAŞA', 'BEŞİKTAŞ', 'BEYKOZ', 'BEYLİKDÜZÜ', 'BEYOĞLU', 'BÜYÜKÇEKMECE', 'ÇATALCA', 'ÇEKMEKÖY', 'ESENLER', 'ESENYURT', 'EYÜP', 'FATİH', 'GAZİOSMANPAŞA', 'GÜNGÖREN', 'KADIKÖY', 'KAĞITHANE', 'KARTAL', 'KÜÇÜKÇEKMECE', 'MALTEPE', 'PENDİK', 'SANCAKTEPE', 'SARIYER', 'SİLİVRİ', 'SULTANBEYLİ', 'SULTANGAZİ', 'ŞİLE', 'ŞİŞLİ', 'TUZLA', 'ÜMRANİYE', 'ÜSKÜDAR', 'ZEYTİNBURNU'], '35': ['ALİAĞA', 'BALÇOVA', 'BAYINDIR', 'BAYRAKLI', 'BERGAMA', 'BEYDAĞ', 'BORNOVA', 'BUCA', 'ÇEŞME', 'ÇİĞLİ', 'DİKİLİ', 'FOÇA', 'GAZİEMİR', 'GÜZELBAHÇE', 'KARABAĞLAR', 'KARABURUN', 'KARŞIYAKA', 'KEMALPAŞA', 'KINIK', 'KİRAZ', 'KONAK', 'MENDERES', 'MENEMEN', 'NARLIDERE', 'ÖDEMİŞ', 'SEFERİHİSAR', 'SELÇUK', 'TİRE', 'TORBALI', 'URLA'], '36': ['AKYAKA', 'ARPAÇAY', 'DİGOR', 'KAĞIZMAN', 'MERKEZ', 'SARIKAMIŞ', 'SELİM', 'SUSUZ'], '37': ['ABANA', 'AĞLI', 'ARAÇ', 'AZDAVAY', 'BOZKURT', 'CİDE', 'ÇATALZEYTİN', 'DADAY', 'DEVREKANİ', 'DOĞANYURT', 'HANÖNÜ', 'İHSANGAZİ', 'İNEBOLU', 'KÜRE', 'MERKEZ', 'PINARBAŞI', 'SEYDİLER', 'ŞENPAZAR', 'TAŞKÖPRÜ', 'TOSYA'], '38': ['AKKIŞLA', 'BÜNYAN', 'DEVELİ', 'FELAHİYE', 'HACILAR', 'İNCESU', 'KOCASİNAN', 'MELİKGAZİ', 'ÖZVATAN', 'PINARBAŞI', 'SARIOĞLAN', 'SARIZ', 'TALAS', 'TOMARZA', 'YAHYALI', 'YEŞİLHİSAR'], '39': ['BABAESKİ', 'DEMİRKÖY', 'KOFÇAZ', 'LÜLEBURGAZ', 'MERKEZ', 'PEHLİVANKÖY', 'PINARHİSAR', 'VİZE'], '40': ['AKÇAKENT', 'AKPINAR', 'BOZTEPE', 'ÇİÇEKDAĞI', 'KAMAN', 'MERKEZ', 'MUCUR'], '41': ['BAŞİSKELE', 'ÇAYIROVA', 'DARICA', 'DERİNCE', 'DİLOVASI', 'GEBZE', 'GÖLCÜK', 'İZMİT', 'KANDIRA', 'KARAMÜRSEL', 'KARTEPE', 'KÖRFEZ'], '42': ['AHIRLI', 'AKÖREN', 'AKŞEHİR', 'ALTINEKİN', 'BEYŞEHİR', 'BOZKIR', 'CİHANBEYLİ', 'ÇELTİK', 'ÇUMRA', 'DERBENT', 'DEREBUCAK', 'DOĞANHİSAR', 'EMİRGAZİ', 'EREĞLİ', 'GÜNEYSINIR', 'HADİM', 'HALKAPINAR', 'HÜYÜK', 'ILGIN', 'KADINHANI', 'KARAPINAR', 'KARATAY', 'KULU', 'MERAM', 'SARAYÖNÜ', 'SELÇUKLU', 'SEYDİŞEHİR', 'TAŞKENT', 'TUZLUKÇU', 'YALIHÜYÜK', 'YUNAK'], '43': ['ALTINTAŞ', 'ASLANAPA', 'ÇAVDARHİSAR', 'DOMANİÇ', 'DUMLUPINAR', 'EMET', 'GEDİZ', 'HİSARCIK', 'MERKEZ', 'PAZARLAR', 'SİMAV', 'ŞAPHANE', 'TAVŞANLI'], '44': ['AKÇADAĞ', 'ARAPGİR', 'ARGUVAN', 'BATTALGAZİ', 'DARENDE', 'DOĞANŞEHİR', 'DOĞANYOL', 'HEKİMHAN', 'KALE', 'KULUNCAK', 'PÜTÜRGE', 'YAZIHAN', 'YEŞİLYURT'], '45': ['AHMETLİ', 'AKHİSAR', 'ALAŞEHİR', 'DEMİRCİ', 'GÖLMARMARA', 'GÖRDES', 'KIRKAĞAÇ', 'KÖPRÜBAŞI', 'KULA', 'SALİHLİ', 'SARIGÖL', 'SARUHANLI', 'SELENDİ', 'SOMA', 'ŞEHZADELER', 'TURGUTLU', 'YUNUSEMRE'], '46': ['AFŞİN', 'ANDIRIN', 'ÇAĞLAYANCERİT', 'DULKADİROĞLU', 'EKİNÖZÜ', 'ELBİSTAN', 'GÖKSUN', 'NURHAK', 'ONİKİŞUBAT', 'PAZARCIK', 'TÜRKOĞLU'], '47': ['ARTUKLU', 'DARGEÇİT', 'DERİK', 'KIZILTEPE', 'MAZIDAĞI', 'MİDYAT', 'NUSAYBİN', 'ÖMERLİ', 'SAVUR', 'YEŞİLLİ'], '48': ['BODRUM', 'DALAMAN', 'DATÇA', 'FETHİYE', 'KAVAKLIDERE', 'KÖYCEĞİZ', 'MARMARİS', 'MENTEŞE', 'MİLAS', 'ORTACA', 'SEYDİKEMER', 'ULA', 'YATAĞAN'], '49': ['BULANIK', 'HASKÖY', 'KORKUT', 'MALAZGİRT', 'MERKEZ', 'VARTO'], '50': ['ACIGÖL', 'AVANOS', 'DERİNKUYU', 'GÜLŞEHİR', 'HACIBEKTAŞ', 'KOZAKLI', 'MERKEZ', 'ÜRGÜP'], '51': ['ALTUNHİSAR', 'BOR', 'ÇAMARDI', 'ÇİFTLİK', 'MERKEZ', 'ULUKIŞLA'], '52': ['AKKUŞ', 'ALTINORDU', 'AYBASTI', 'ÇAMAŞ', 'ÇATALPINAR', 'ÇAYBAŞI', 'FATSA', 'GÖLKÖY', 'GÜLYALI', 'GÜRGENTEPE', 'İKİZCE', 'KABADÜZ', 'KABATAŞ', 'KORGAN', 'KUMRU', 'MESUDİYE', 'PERŞEMBE', 'ULUBEY', 'ÜNYE'], '53': ['ARDEŞEN', 'ÇAMLIHEMŞİN', 'ÇAYELİ', 'DEREPAZARI', 'FINDIKLI', 'GÜNEYSU', 'HEMŞİN', 'İKİZDERE', 'İYİDERE', 'KALKANDERE', 'MERKEZ', 'PAZAR'], '54': ['ADAPAZARI', 'AKYAZI', 'ARİFİYE', 'ERENLER', 'FERİZLİ', 'GEYVE', 'HENDEK', 'KARAPÜRÇEK', 'KARASU', 'KAYNARCA', 'KOCAALİ', 'PAMUKOVA', 'SAPANCA', 'SERDİVAN', 'SÖĞÜTLÜ', 'TARAKLI'], '55': ['19 MAYIS', 'ALAÇAM', 'ASARCIK', 'ATAKUM', 'AYVACIK', 'BAFRA', 'CANİK', 'ÇARŞAMBA', 'HAVZA', 'İLKADIM', 'KAVAK', 'LADİK', 'SALIPAZARI', 'TEKKEKÖY', 'TERME', 'VEZİRKÖPRÜ', 'YAKAKENT'], '56': ['BAYKAN', 'ERUH', 'KURTALAN', 'MERKEZ', 'PERVARİ', 'ŞİRVAN', 'TİLLO'], '57': ['AYANCIK', 'BOYABAT', 'DİKMEN', 'DURAĞAN', 'ERFELEK', 'GERZE', 'MERKEZ', 'SARAYDÜZÜ', 'TÜRKELİ'], '58': ['AKINCILAR', 'ALTINYAYLA', 'DİVRİĞİ', 'DOĞANŞAR', 'GEMEREK', 'GÖLOVA', 'GÜRÜN', 'HAFİK', 'İMRANLI', 'KANGAL', 'KOYULHİSAR', 'MERKEZ', 'SUŞEHRİ', 'ŞARKIŞLA', 'ULAŞ', 'YILDIZELİ', 'ZARA'], '59': ['ÇERKEZKÖY', 'ÇORLU', 'ERGENE', 'HAYRABOLU', 'KAPAKLI', 'MALKARA', 'MARMARAEREĞLİSİ', 'MURATLI', 'SARAY', 'SÜLEYMANPAŞA', 'ŞARKÖY'], '60': ['ALMUS', 'ARTOVA', 'BAŞÇİFTLİK', 'ERBAA', 'MERKEZ', 'NİKSAR', 'PAZAR', 'REŞADİYE', 'SULUSARAY', 'TURHAL', 'YEŞİLYURT', 'ZİLE'], '61': ['AKÇAABAT', 'ARAKLI', 'ARSİN', 'BEŞİKDÜZÜ', 'ÇARŞIBAŞI', 'ÇAYKARA', 'DERNEKPAZARI', 'DÜZKÖY', 'HAYRAT', 'KÖPRÜBAŞI', 'MAÇKA', 'OF', 'ORTAHİSAR', 'SÜRMENE', 'ŞALPAZARI', 'TONYA', 'VAKFIKEBİR', 'YOMRA'], '62': ['ÇEMİŞGEZEK', 'HOZAT', 'MAZGİRT', 'MERKEZ', 'NAZIMİYE', 'OVACIK', 'PERTEK', 'PÜLÜMÜR'], '63': ['AKÇAKALE', 'BİRECİK', 'BOZOVA', 'CEYLANPINAR', 'EYYÜBİYE', 'HALFETİ', 'HALİLİYE', 'HARRAN', 'HİLVAN', 'KARAKÖPRÜ', 'SİVEREK', 'SURUÇ', 'VİRANŞEHİR'], '64': ['BANAZ', 'EŞME', 'KARAHALLI', 'MERKEZ', 'SİVASLI', 'ULUBEY'], '65': ['BAHÇESARAY', 'BAŞKALE', 'ÇALDIRAN', 'ÇATAK', 'EDREMİT', 'ERCİŞ', 'GEVAŞ', 'GÜRPINAR', 'İPEKYOLU', 'MURADİYE', 'ÖZALP', 'SARAY', 'TUŞBA'], '66': ['AKDAĞMADENİ', 'AYDINCIK', 'BOĞAZLIYAN', 'ÇANDIR', 'ÇAYIRALAN', 'ÇEKEREK', 'KADIŞEHRİ', 'MERKEZ', 'SARAYKENT', 'SARIKAYA', 'SORGUN', 'ŞEFAATLİ', 'YENİFAKILI', 'YERKÖY'], '67': ['ALAPLI', 'ÇAYCUMA', 'DEVREK', 'EREĞLİ', 'GÖKÇEBEY', 'KİLİMLİ', 'KOZLU', 'MERKEZ'], '68': ['AĞAÇÖREN', 'ESKİL', 'GÜLAĞAÇ', 'GÜZELYURT', 'MERKEZ', 'ORTAKÖY', 'SARIYAHŞİ'], '69': ['AYDINTEPE', 'DEMİRÖZÜ', 'MERKEZ'], '70': ['AYRANCI', 'BAŞYAYLA', 'ERMENEK', 'KAZIMKARABEKİR', 'MERKEZ', 'SARIVELİLER'], '71': ['BAHŞİLİ', 'BALIŞEYH', 'ÇELEBİ', 'DELİCE', 'KARAKEÇİLİ', 'KESKİN', 'MERKEZ', 'SULAKYURT', 'YAHŞİHAN'], '72': ['BEŞİRİ', 'GERCÜŞ', 'HASANKEYF', 'KOZLUK', 'MERKEZ', 'SASON'], '73': ['BEYTÜŞŞEBAP', 'CİZRE', 'GÜÇLÜKONAK', 'İDİL', 'MERKEZ', 'SİLOPİ', 'ULUDERE'], '74': ['AMASRA', 'KURUCAŞİLE', 'MERKEZ', 'ULUS'], '75': ['ÇILDIR', 'DAMAL', 'GÖLE', 'HANAK', 'MERKEZ', 'POSOF'], '76': ['ARALIK', 'KARAKOYUNLU', 'MERKEZ', 'TUZLUCA'], '77': ['ALTINOVA', 'ARMUTLU', 'ÇINARCIK', 'ÇİFTLİKKÖY', 'MERKEZ', 'TERMAL'], '78': ['EFLANİ', 'ESKİPAZAR', 'MERKEZ', 'OVACIK', 'SAFRANBOLU', 'YENİCE'], '79': ['ELBEYLİ', 'MERKEZ', 'MUSABEYLİ', 'POLATELİ'], '80': ['BAHÇE', 'DÜZİÇİ', 'HASANBEYLİ', 'KADİRLİ', 'MERKEZ', 'SUMBAS', 'TOPRAKKALE'], '81': ['AKÇAKOCA', 'CUMAYERİ', 'ÇİLİMLİ', 'GÖLYAKA', 'GÜMÜŞOVA', 'KAYNAŞLI', 'MERKEZ', 'YIĞILCA']}

from address.models import Country, City, Township

country = Country.objects.create(name='Türkiye')

for city in cities.values():
    City.objects.create(country=country, name=city)

for id, towns in townships.items():
    city = City.objects.get(name=cities[id])
    for t in towns:
        Township.objects.create(city=city, name=t)
"""********************************************************************"""
"""******************** USER MIGRATION *****************************"""
"""********************************************************************"""
STORE_NAMES = ["Kardeşler OtoYıkama", "İsmail otoyıkama", "Turan Otoyıkama", "Ceylan Oto yıkama",
               "Kadircan Otoyıkama", "Güleç Yıkama", "Çelik Otoyıkama", "Ahmet Yıkama"]
from users.service import UserService
from users.enums import GroupType
from address.service import AddressService
from stores.service import StoreService
from cars.service import CarService
from cars.enums import CarType


for number in range(100):
    service = UserService()
    car_service = CarService()
    data = {
        "first_name": "Customer {}".format(number),
        "last_name": "LastCustomer",
        "phone_number": "555111{}".format(number),
        "group_type": GroupType.customer
    }
    customer, _ = service.get_or_create_user(**data)
    customer_profile = customer.customer_profile
    car_types = [CarType.sedan, CarType.suv, CarType.commercial]
    for k in range(3):
        car_data = {
            "licence_plate": f"34A00{k}",
            "customer_profile": customer_profile,
            "car_type": car_types[k]
        }
        car = car_service.create_car(**car_data)
    print("{}/1000 customer completed".format(number + 1))

for number in range(2000):
    service = UserService()
    store_service = StoreService()
    data = {
        "first_name": "Washer {}".format(number),
        "last_name": "LastWasher",
        "phone_number": "555333{}".format(number),
        "group_type": GroupType.washer
    }
    user, _ = service.get_or_create_user(**data)

    for number2 in range(randint(1, 3)):
        store_data = {
            "name": STORE_NAMES[randint(0, 7)],
            "washer_profile": user.washer_profile,
            "phone_number": data["phone_number"],
            "tax_office": "Tax Washer {} Store {}".format(number, number2),
            "tax_number": randint(1000, 9999),
            "latitude": randint(36, 42) + random(),
            "longitude": randint(26, 45) + random(),
        }
        config_data = {
            "opening_hours": {
                "monday": {
                    "start": "{}:{}".format(randint(7, 10), randint(0, 59)),
                    "end": "{}:{}".format(randint(18, 21), randint(0, 59))
                },
                "tuesday": {
                    "start": "{}:{}".format(randint(7, 10), randint(0, 59)),
                    "end": "{}:{}".format(randint(18, 21), randint(0, 59))
                },
                "wednesday": {
                    "start": "{}:{}".format(randint(7, 10), randint(0, 59)),
                    "end": "{}:{}".format(randint(18, 21), randint(0, 59))
                },
                "thursday": {
                    "start": "{}:{}".format(randint(7, 10), randint(0, 59)),
                    "end": "{}:{}".format(randint(18, 21), randint(0, 59))
                },
                "friday": {
                    "start": "{}:{}".format(randint(7, 10), randint(0, 59)),
                    "end": "{}:{}".format(randint(18, 21), randint(0, 59))
                },
                "saturday": {
                    "start": "{}:{}".format(randint(7, 10), randint(0, 59)),
                    "end": "{}:{}".format(randint(18, 21), randint(0, 59))
                },
                "sunday": {
                    "start": None,
                    "end": None
                }
            },
            "reservation_hours": {
                "monday": {
                    "start": "{}:{}".format(randint(13, 16), 0),
                    "end": "{}:{}".format(randint(17, 19), 0)
                },
                "tuesday": {
                    "start": "{}:{}".format(randint(13, 16), 0),
                    "end": "{}:{}".format(randint(17, 19), 0)
                },
                "wednesday": {
                    "start": "{}:{}".format(randint(13, 16), 0),
                    "end": "{}:{}".format(randint(17, 19), 0)
                },
                "thursday": {
                    "start": "{}:{}".format(randint(13, 16), 0),
                    "end": "{}:{}".format(randint(17, 19), 0)
                },
                "friday": {
                    "start": "{}:{}".format(randint(13, 16), 0),
                    "end": "{}:{}".format(randint(17, 19), 0)
                },
                "saturday": {
                    "start": "{}:{}".format(randint(13, 16), 0),
                    "end": "{}:{}".format(randint(17, 19), 0)
                },
                "sunday": {
                    "start": None,
                    "end": None
                }
            }
        }
        store = store_service.create_store(**store_data)
        store.config = config_data
        store.is_approved = randint(0, 1)
        store.save()
        address_service = AddressService()
        country = Country.objects.first()
        city = country.city_set.all()[randint(0, country.city_set.all().count() - 1)]
        township = city.township_set.all()[randint(0, city.township_set.all().count() - 1)]
        address_service.create_address(store, country, city, township,
                                       line="line {}".format(store.pk),
                                       postcode="000{}".format(store.pk))

        for number3 in range(randint(2,5)):
            service = UserService()
            data = {
                "first_name": "Washer {} - Worker {}".format(number, number3),
                "last_name": "LastWorker",
                "phone_number": "555222{}{}{}".format(number, number2, number3),
                "group_type": GroupType.worker
            }
            worker, _ = service.get_or_create_user(**data)
            wp = worker.worker_profile
            wp.washer_profile = user.washer_profile
            wp.store = store
            wp.save()
    print("{}/2000 washer completed".format(number + 1))

print("indexing stores...")
from search.indexer import StoreIndexer
service = StoreIndexer()
service.index_stores()