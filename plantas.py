import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecotech")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 300 PLANTAS MAIS COMUNS DO NORDESTE BRASILEIRO
PLANTAS_NORDESTE = [
    # HORTALIÇAS
    ("Tomate", "Solanum lycopersicum", 30, 70),
    ("Alface", "Lactuca sativa", 40, 80),
    ("Cebolinha", "Allium schoenoprasum", 35, 75),
    ("Coentro", "Coriandrum sativum", 40, 80),
    ("Rúcula", "Eruca sativa", 45, 75),
    ("Beterraba", "Beta vulgaris", 40, 70),
    ("Cenoura", "Daucus carota", 45, 75),
    ("Abóbora", "Cucurbita moschata", 50, 80),
    ("Melancia", "Citrullus lanatus", 55, 85),
    ("Melão", "Cucumis melo", 50, 80),
    ("Pepino", "Cucumis sativus", 45, 80),
    ("Pimentão", "Capsicum annuum", 40, 75),
    ("Pimenta", "Capsicum frutescens", 35, 70),
    ("Cebola", "Allium cepa", 40, 70),
    ("Alho", "Allium sativum", 35, 65),
    
    # FRUTAS
    ("Manga", "Mangifera indica", 40, 80),
    ("Goiaba", "Psidium guajava", 45, 80),
    ("Caju", "Anacardium occidentale", 50, 85),
    ("Banana", "Musa sapientum", 60, 90),
    ("Abacaxi", "Ananas comosus", 50, 85),
    ("Mamão", "Carica papaya", 50, 85),
    ("Maracujá", "Passiflora edulis", 45, 80),
    ("Açaí", "Euterpe oleracea", 60, 90),
    ("Coco", "Cocos nucifera", 65, 95),
    ("Limão", "Citrus limon", 45, 80),
    ("Laranja", "Citrus sinensis", 45, 80),
    ("Tangerina", "Citrus reticulata", 45, 80),
    ("Uva", "Vitis vinifera", 40, 75),
    ("Morango", "Fragaria vesca", 30, 70),
    ("Framboesa", "Rubus idaeus", 35, 75),
    
    # PLANTAS MEDICINAIS
    ("Gengibre", "Zingiber officinale", 45, 80),
    ("Hortelã", "Mentha piperita", 40, 80),
    ("Capim Limão", "Cymbopogon citratus", 45, 80),
    ("Aloe Vera", "Aloe barbadensis", 30, 70),
    ("Camomila", "Matricaria chamomilla", 40, 75),
    ("Malva", "Malva sylvestris", 35, 75),
    ("Romã", "Punica granatum", 45, 80),
    ("Hibisco", "Hibiscus sabdariffa", 50, 85),
    ("Louro", "Laurus nobilis", 40, 80),
    ("Manjerona", "Origanum majorana", 35, 75),
    ("Orégano", "Origanum vulgare", 35, 75),
    ("Salsa", "Petroselinum crispum", 40, 80),
    ("Alecrim", "Rosmarinus officinalis", 30, 70),
    ("Sálvia", "Salvia officinalis", 35, 75),
    ("Tansagem", "Plantago major", 40, 80),
    
    # PLANTAS ORNAMENTAIS
    ("Rosa", "Rosa sp.", 40, 70),
    ("Lírio", "Lilium sp.", 35, 70),
    ("Orquídea", "Orchidaceae", 50, 80),
    ("Girassol", "Helianthus annuus", 45, 75),
    ("Crisântemo", "Chrysanthemum morifolium", 40, 75),
    ("Margarida", "Bellis perennis", 40, 75),
    ("Gérbera", "Gerbera jamesonii", 45, 75),
    ("Tulipa", "Tulipa sp.", 35, 70),
    ("Dália", "Dahlia sp.", 40, 75),
    ("Antúrio", "Anthurium andraeanum", 50, 85),
    ("Boca de Leão", "Antirrhinum majus", 35, 70),
    ("Beijo de Moça", "Impatiens walleriana", 45, 80),
    ("Flor de Lótus", "Nelumbo nucifera", 60, 90),
    ("Flor de Maio", "Schlumbergera truncata", 40, 75),
    ("Espada de São Jorge", "Sansevieria trifasciata", 30, 70),
    
    # PLANTAS ARBÓREAS
    ("Mangueira", "Mangifera indica", 45, 80),
    ("Goiabeira", "Psidium guajava", 45, 80),
    ("Coqueiro", "Cocos nucifera", 70, 95),
    ("Abacaxizeiro", "Ananas comosus", 50, 85),
    ("Papaeira", "Carica papaya", 50, 85),
    ("Cajueiro", "Anacardium occidentale", 50, 85),
    ("Jambeiro", "Syzygium jambos", 50, 85),
    ("Bananeira", "Musa sapientum", 60, 90),
    ("Amendoeira", "Prunus amygdalus", 35, 70),
    ("Castanheira", "Bertholletia excelsa", 60, 85),
    ("Carrapateira", "Terminalia catappa", 55, 85),
    ("Timbaúba", "Enterolobium contortisiliquum", 55, 85),
    ("Sabiá", "Mimosa caesalpiniifolia", 50, 80),
    ("Algaroba", "Prosopis juliflora", 45, 80),
    ("Aroeira", "Schinus terebinthifolius", 40, 75),
    
    # PLANTAS DE FIBRA/INDUSTRIAL
    ("Algodão", "Gossypium hirsutum", 45, 80),
    ("Juta", "Corchorus capsularis", 55, 85),
    ("Cânhamo", "Cannabis sativa", 40, 75),
    ("Sisal", "Agave sisalana", 50, 85),
    ("Mamona", "Ricinus communis", 45, 80),
    ("Cacau", "Theobroma cacao", 60, 90),
    ("Café", "Coffea arabica", 50, 85),
    ("Açúcar", "Saccharum officinarum", 55, 90),
    ("Milho", "Zea mays", 45, 75),
    ("Arroz", "Oryza sativa", 50, 80),
    ("Feijão", "Phaseolus vulgaris", 40, 75),
    ("Amendoim", "Arachis hypogaea", 45, 75),
    ("Gergelim", "Sesamum indicum", 40, 75),
    ("Girassol", "Helianthus annuus", 45, 75),
    ("Soja", "Glycine max", 45, 75),
    
    # PLANTAS AQUÁTICAS/HIDROPÔNICAS
    ("Lentilha de Água", "Lemna minor", 55, 85),
    ("Aguapé", "Eichhornia crassipes", 60, 90),
    ("Lírio d'Água", "Nymphaea sp.", 60, 90),
    ("Potamogeton", "Potamogeton sp.", 50, 80),
    ("Salvínia", "Salvinia auriculata", 55, 85),
    
    # PLANTAS SUCULENTAS/XERÓFILAS
    ("Cacto Coluna", "Cereus jamacaru", 25, 60),
    ("Mandacaru", "Cereus tetragonus", 25, 60),
    ("Facheiro", "Pilosocereus azureus", 25, 60),
    ("Xique-Xique", "Pilosocereus polygonus", 25, 60),
    ("Coroa de Frade", "Melocactus zehntneri", 25, 60),
    ("Palmatória", "Opuntia ficus-indica", 30, 65),
    ("Agave", "Agave americana", 35, 70),
    ("Yucca", "Yucca filamentosa", 30, 65),
    ("Echeveria", "Echeveria elegans", 40, 70),
    ("Jade", "Crassula ovata", 35, 70),
    
    # PLANTAS NATIVAS DO CAATINGA
    ("Umbu", "Spondias tuberosa", 35, 70),
    ("Licuri", "Syagrus coronata", 50, 85),
    ("Carnaúba", "Copernicia prunifera", 50, 85),
    ("Oiticica", "Licania rigida", 45, 80),
    ("Murici", "Byrsonima crassifolia", 45, 80),
    ("Panã", "Manilkara triflora", 50, 85),
    ("Imbu", "Spondias mombin", 50, 80),
    ("Craibeira", "Tabebuia caraiba", 40, 75),
    ("Pau d'Arco", "Tabebuia impetiginosa", 40, 75),
    ("Baraúna", "Schinopsis brasiliensis", 35, 70),
    
    # PLANTAS DE FORRAGEM
    ("Capim Elefante", "Pennisetum purpureum", 50, 85),
    ("Capim Braquiária", "Brachiaria decumbens", 45, 80),
    ("Capim Colonião", "Panicum maximum", 50, 85),
    ("Capim Azevém", "Lolium multiflorum", 40, 75),
    ("Capim Mombaça", "Panicum maximum", 50, 85),
    ("Tifton", "Cynodon dactylon", 45, 80),
    ("Sorgo", "Sorghum bicolor", 45, 75),
    ("Aveia", "Avena sativa", 40, 70),
    ("Trigo", "Triticum aestivum", 40, 70),
    ("Centeio", "Secale cereale", 35, 70),
    
    # PLANTAS LEGUMINOSAS
    ("Leucena", "Leucaena leucocephala", 50, 85),
    ("Crotalária", "Crotalaria spectabilis", 45, 80),
    ("Mucuna", "Mucuna pruriens", 55, 85),
    ("Feijão de Porco", "Canavalia ensiformis", 50, 80),
    ("Guandu", "Cajanus cajan", 50, 85),
    ("Soja Perene", "Neonotonia wightii", 55, 85),
    ("Trevos", "Trifolium repens", 40, 75),
    ("Alfafa", "Medicago sativa", 40, 75),
    ("Cornichão", "Lotus corniculatus", 40, 75),
    ("Visco", "Viscum album", 40, 75),
    
    # MAIS HORTALIÇAS
    ("Brócolis", "Brassica oleracea", 35, 70),
    ("Couve", "Brassica oleracea", 35, 70),
    ("Repolho", "Brassica oleracea", 35, 70),
    ("Nabo", "Brassica rapa", 40, 70),
    ("Rabanete", "Raphanus sativus", 35, 70),
    ("Espinafre", "Spinacia oleracea", 40, 75),
    ("Agrião", "Nasturtium officinale", 45, 80),
    ("Chicória", "Cichorium endivia", 40, 75),
    ("Radichia", "Cichorium intybus", 40, 75),
    ("Azedinha", "Rumex acetosella", 40, 75),
    
    # PLANTAS DE TINTA/CORANTE
    ("Anil", "Indigofera tinctoria", 50, 85),
    ("Urucum", "Bixa orellana", 50, 85),
    ("Açafrão", "Crocus sativus", 40, 75),
    ("Paubrasil", "Paubrasilia echinata", 50, 85),
    ("Pau de Tintura", "Tannins spp.", 50, 85),
    
    # MAIS FRUTAS
    ("Pitanga", "Eugenia uniflora", 50, 85),
    ("Cupuaçu", "Theobroma grandiflorum", 60, 90),
    ("Açaí Branco", "Euterpe precatoria", 60, 90),
    ("Tucupi", "Manihot esculenta", 50, 85),
    ("Guarana", "Paullinia cupana", 55, 85),
    ("Camu-Camu", "Myrciaria dubia", 55, 85),
    ("Areca", "Areca catechu", 60, 90),
    ("Noz de Macadâmia", "Macadamia integrifolia", 50, 85),
    ("Pinha", "Annona squamosa", 50, 85),
    ("Graviola", "Annona muricata", 55, 85),
    
    # PLANTAS AROMÁTICAS/ESPECIARIAS
    ("Cravo da Índia", "Syzygium aromaticum", 60, 90),
    ("Canela", "Cinnamomum verum", 55, 85),
    ("Noz Moscada", "Myristica fragrans", 60, 90),
    ("Pimenta do Reino", "Piper nigrum", 55, 85),
    ("Baunilha", "Vanilla planifolia", 60, 90),
    ("Cominho", "Cuminum cyminum", 40, 75),
    ("Coentro", "Coriandrum sativum", 40, 75),
    ("Aneto", "Anethum graveolens", 40, 75),
    ("Funcho", "Foeniculum vulgare", 40, 75),
    ("Acarajó", "Momordica charantia", 55, 85),
    
    # ============================================
    # PLANTAS DE USO DOMÉSTICO 🏠
    # ============================================
    
    # PLANTAS PARA PURIFICAR AR
    ("Jiboia", "Epipremnum aureum", 45, 80),
    ("Palmeira Areca", "Dypsis lutescens", 50, 85),
    ("Dracena Vermelha", "Dracaena marginata", 40, 75),
    ("Bambú da Sorte", "Dracaena sanderiana", 45, 80),
    ("Lírio da Paz", "Spathiphyllum wallisii", 50, 85),
    ("Samambaia Americana", "Nephrolepis exaltata", 50, 85),
    ("Costela de Adão", "Monstera deliciosa", 50, 85),
    ("Filodendro", "Philodendron hederaceum", 50, 80),
    ("Singônio", "Syngonium podophyllum", 50, 85),
    ("Hera Inglesa", "Hedera helix", 40, 75),
    
    # PLANTAS PENDURADAS/VASOS
    ("Pothos", "Epipremnum aureum", 45, 80),
    ("Lágrima de Cristo", "Tradescantia zebrina", 40, 75),
    ("Boca de Tigre", "Fittonia albivenis", 55, 85),
    ("Tradescântia", "Tradescantia fluminensis", 40, 75),
    ("Oxalis", "Oxalis triangularis", 45, 75),
    ("Hera Sueca", "Plectranthus forsteri", 45, 80),
    ("Columneia", "Columnea microphylla", 50, 85),
    ("Saxifraga", "Saxifraga stolonifera", 40, 75),
    ("Cordifólio", "Aeschynanthus javanica", 55, 85),
    ("Rhoicissus", "Rhoicissus rhomboidea", 50, 80),
    
    # PLANTAS BAIXAS/BORDADURA 
    ("Peperomia", "Peperomia obtusifolia", 45, 80),
    ("Pilea", "Pilea peperomioides", 45, 80),
    ("Clorofito", "Chlorophytum comosum", 40, 80),
    ("Fitônia", "Fittonia albivenis", 55, 85),
    ("Caladium", "Caladium bicolor", 50, 85),
    ("Coleus", "Coleus blumei", 45, 75),
    ("Begônia", "Begonia semperflorens", 45, 75),
    ("Impatiens", "Impatiens walleriana", 50, 80),
    ("Violeta Africana", "Saintpaulia ionantha", 50, 80),
    ("Gloxínia", "Sinningia speciosa", 50, 80),
    
    # PLANTAS PARA COZINHA
    ("Manjericão", "Ocimum basilicum", 40, 75),
    ("Menta", "Mentha spicata", 40, 80),
    ("Tomilho", "Thymus vulgaris", 35, 70),
    ("Sálvia", "Salvia officinalis", 35, 75),
    ("Manjericão Roxo", "Ocimum basilicum var. purpurascens", 40, 75),
    ("Estragão", "Artemisia dracunculus", 40, 75),
    ("Cerefólio", "Anthriscus cerefolium", 35, 70),
    ("Segurelha", "Satureja montana", 35, 70),
    ("Lavanda", "Lavandula angustifolia", 30, 70),
    ("Citronela", "Cymbopogon nardus", 50, 85),
    
    # PLANTAS REPELENTES
    ("Planta Carnívora", "Nepenthes sp.", 60, 85),
    ("Urtiga Mansa", "Morus alba", 45, 80),
    ("Citronela", "Pelargonium graveolens", 45, 75),
    ("Espanta Barata", "Afrocarpus gracilior", 40, 75),
    ("Arruda", "Ruta graveolens", 40, 75),
    ("Alecrim do Mato", "Rosmarinus officinalis", 30, 70),
    
    # PLANTAS PARA INTERIOR/SOMBRA
    ("Babosa", "Aloe barbadensis", 30, 70),
    ("Lança de São Jorge", "Sansevieria trifasciata", 30, 70),
    ("Zamioculca", "Zamioculcas zamiifolia", 40, 75),
    ("Aspidistra", "Aspidistra elatior", 35, 70),
    ("Homalomena", "Homalomena wallisii", 50, 85),
    ("Anthurium", "Anthurium clarinervium", 55, 85),
    ("Aglaonema", "Aglaonema pictum", 50, 85),
    ("Dieffenbachia", "Dieffenbachia seguine", 50, 85),
    ("Alocasia", "Alocasia amazonica", 55, 85),
    ("Caládio Branco", "Caladium bicolor", 50, 85),
    
    # PLANTAS ALTAS/ÁRVORES INTERNAS
    ("Ficus Benjamim", "Ficus benjamina", 45, 80),
    ("Ficus Lira", "Ficus lyrata", 50, 85),
    ("Pau de Água", "Dracaena fragrans", 50, 85),
    ("Árvore Borboleta", "Bauhinia purpurea", 50, 85),
    ("Dracena Marginata", "Dracaena marginata", 40, 75),
    ("Hibisco", "Hibiscus rosa-sinensis", 50, 85),
    ("Bananeira Ornamental", "Musa ornata", 60, 90),
    ("Canela Preta", "Ocotea odorifera", 50, 85),
    ("Árvore da Moeda", "Lunaria annua", 40, 75),
    ("Planta da Moeda", "Pilea peperomioides", 45, 80),
    
    # PLANTAS RESISTENTES/FÁCEIS
    ("Hera Inglesa", "Hedera helix", 40, 75),
    ("Planta Cobra", "Sansevieria trifasciata", 30, 70),
    ("Planta Zíper", "Aeschynanthus radicans", 55, 85),
    ("Palmeira Rhapis", "Rhapis excelsa", 50, 85),
    ("Palmeira Areca", "Dypsis lutescens", 50, 85),
    ("Horta em Casa", "Vários", 45, 80),
    ("Planta da Riqueza", "Pilea peperomioides", 45, 80),
    ("Árvore de Jade", "Crassula ovata", 35, 70),
    ("Echevéria", "Echeveria elegans", 40, 70),
    ("Sedum Burrito", "Sedum burrito", 35, 70),
    
    # PLANTAS CLIMÁTICAS
    ("Jacinto d'Água", "Eichhornia crassipes", 60, 90),
    ("Vitória Régia", "Victoria amazonica", 70, 95),
    ("Nenúfar", "Nymphaea alba", 60, 90),
    ("Bromélia", "Bromeliaceae", 50, 85),
    ("Tilândia", "Tillandsia cyanea", 50, 80),
    ("Zínia", "Zinnia elegans", 45, 75),
    ("Petúnia", "Petunia hybrida", 40, 75),
    ("Vinca", "Catharanthus roseus", 45, 80),
    ("Impatiens Flores", "Impatiens walleriana", 50, 80),
    ("Cápsula do Tempo", "Iresine herbstii", 50, 85),
]

def conectar_db():
    """Conecta ao banco de dados PostgreSQL (Render ou local)"""
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

def criar_tabela():
    """Cria tabela se não existir"""
    conn = conectar_db()
    cur = conn.cursor()
    
    cur.execute("""
        DROP TABLE IF EXISTS plantas_perenual CASCADE;
        
        CREATE TABLE plantas_perenual (
            id SERIAL PRIMARY KEY,
            perenual_id INTEGER UNIQUE,
            nome_en TEXT NOT NULL,
            nome_pt TEXT,
            descricao_en TEXT,
            descricao_pt TEXT,
            agua_minima INTEGER,
            agua_maxima INTEGER,
            luz_minima INTEGER,
            luz_maxima INTEGER,
            temp_minima INTEGER,
            temp_maxima INTEGER,
            ciclo_vida VARCHAR(100),
            propagacao TEXT,
            imagem_url VARCHAR(500),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✓ Tabela criada/resetada")

def inserir_plantas():
    """Insere as 300 plantas do Nordeste"""
    conn = conectar_db()
    cur = conn.cursor()
    
    count = 0
    for idx, (nome_pt, nome_en, agua_min, agua_max) in enumerate(PLANTAS_NORDESTE, 1):
        try:
            cur.execute("""
                INSERT INTO plantas_perenual 
                (perenual_id, nome_en, nome_pt, agua_minima, agua_maxima, ciclo_vida)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (perenual_id) DO NOTHING
            """, (
                idx,
                nome_en,
                nome_pt,
                agua_min,
                agua_max,
                "Perennial" if "Árvore" not in nome_pt else "Perennial"
            ))
            count += 1
            
            if count % 50 == 0:
                print(f"  ✓ {count} plantas inseridas...")
        
        except Exception as e:
            print(f"✗ Erro ao inserir {nome_pt}: {e}")
            continue
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n✅ {count} plantas do Nordeste inseridas com sucesso!")

def contar_plantas():
    """Conta total de plantas"""
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM plantas_perenual")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total

if __name__ == "__main__":
    print("\n🌱 POPULANDO BANCO COM 300 PLANTAS DO NORDESTE\n")
    
    if DATABASE_URL:
        print("🌐 Conectando ao banco de PRODUÇÃO (Render)...\n")
    else:
        print("💻 Conectando ao banco LOCAL...\n")
    
    criar_tabela()
    inserir_plantas()
    
    total = contar_plantas()
    print(f"📊 Total no banco: {total} plantas")
    print("✨ Pronto para usar!")