"""
This is a temporary file until we upgarde the RDM to v13.
The v12 schema does not contain all information.
"""

TEMP_INSTITUTIONS = [
    {
        "id": "agritec-vyzkum-slechteni-sluzby",
        "props": {"ICO": "48392952", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03jz5v392",
            "URL": "http://www.agritec.cz/",
        },
        "title": {
            "cs": "AGRITEC, výzkum, šlechtění, služby",
            "en": "AGRITEC Research, Breeding and Services",
        },
    },
    {
        "id": "avss-agritec-plant-research",
        "props": {"ICO": "26784246", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/03jz5v392"},
        "title": {"cs": "Agritec Plant Research"},
    },
    {
        "id": "agrotest-fyto",
        "props": {"ICO": "25328859", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04rrs1z45",
            "URL": "http://www.vukrom.cz/",
        },
        "title": {"cs": "Agrotest fyto"},
    },
    {
        "id": "chmelarsky-institut",
        "props": {"ICO": "14864347", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01mkmmc36",
            "URL": "http://www.chizatec.cz/",
        },
        "title": {"cs": "Chmelařský institut", "en": "Hop Research Institute"},
    },
    {
        "id": "nipos",
        "props": {"ICO": "14450551", "acronym": "NIPOS", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01pzyyx54",
            "URL": "http://www.nipos-mk.cz/",
        },
        "title": {
            "cs": "Národní informační a poradenské středisko pro kulturu",
            "en": "National Information and Consulting Centre for Culture",
        },
    },
    {
        "id": "oseva",
        "props": {"ICO": "26791251", "acronym": "Oseva", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0379e1d13",
            "URL": "http://www.oseva-vav.cz",
        },
        "title": {"cs": "OSEVA vývoj a výzkum", "en": "OSEVA Development and Research"},
    },
    {
        "id": "ustr",
        "props": {"ICO": "75112779", "acronym": "ÚSTR", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04ef3fk55",
            "URL": "http://www.ustrcr.cz/",
        },
        "title": {
            "cs": "Ústav pro studium totalitních režimů",
            "en": "Institute for the Study of Totalitarian Regimes",
        },
    },
    {
        "id": "vyzkumny-a-vyvojovy-ustav-drevarsky-praha",
        "nonpreferredLabels": [{"cs": "Dřevařský ústav"}],
        "props": {"ICO": "00014125", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02phgvp38", "URL": "http://www.vvud.cz"},
        "title": {
            "cs": "Výzkumný a vývojový ústav dřevařský, Praha",
            "en": "Timber Research and Development Institute, Prague",
        },
    },
    {
        "id": "cdv",
        "props": {"ICO": "44994575", "acronym": "CDV", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/03rqbe322", "URL": "http://www.cdv.cz/"},
        "title": {
            "cs": "Centrum dopravního výzkumu",
            "en": "Transport Research Centre",
        },
    },
    {
        "id": "centrum-pro-studium-vysokeho-skolstvi",
        "props": {"ICO": "00237752", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/009wgvk87",
            "URL": "http://www.csvs.cz/",
        },
        "title": {
            "cs": "Centrum pro studium vysokého školství",
            "en": "Centre for Higher Education Studies",
        },
    },
    {
        "id": "ustav-archeologicke-pamatkove-pece-severozapadnich-cech",
        "props": {"ICO": "47325011", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01abd7j14",
            "URL": "http://www.uappmost.cz/wp/",
        },
        "title": {
            "cs": "Ústav archeologické památkové péče severozápadních Čech",
            "en": "Institute of Archeological and Cultural Heritage Preservation in Northwestern Bohemia",
        },
    },
    {
        "id": "vubp",
        "props": {"ICO": "00025950", "acronym": "VÚBP", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03zbxqj79",
            "URL": "http://www.vubp.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav bezpečnosti práce",
            "en": "Occupational Safety Research Institute",
        },
    },
    {
        "id": "vugtk",
        "props": {"ICO": "00025615", "acronym": "VÚGTK", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04fgffc11",
            "URL": "http://www.vugtk.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav geodetický, topografický a kartografický",
            "en": "Research Institute of Geodesy, Topography and Cartography",
        },
    },
    {
        "id": "vulhm",
        "props": {"ICO": "00020702", "acronym": "VÚLHM", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/034cj1z12",
            "URL": "http://www.vulhm.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav lesního hospodářství a myslivosti",
            "en": "Forestry and Game Management Research Institute",
        },
    },
    {
        "id": "vupp",
        "props": {"ICO": "00027022", "acronym": "VÚPP", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02jdepa55", "URL": "http://www.vupp.cz"},
        "title": {
            "cs": "Výzkumný ústav potravinářský Praha",
            "en": "Food Research Institute Prague",
        },
    },
    {
        "id": "vupsv",
        "props": {"ICO": "45773009", "acronym": "VÚPSV", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01gccqc59",
            "URL": "http://www.vupsv.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav práce a sociálních věcí",
            "en": "Research Institute for Labour and Social Affairs",
        },
    },
    {
        "id": "vurv",
        "props": {"ICO": "00027006", "acronym": "VÚRV", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0436mv865",
            "URL": "http://www.vurv.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav rostlinné výroby",
            "en": "Crop Research Institute",
        },
    },
    {
        "id": "vyzkumny-ustav-silva-taroucy-pro-krajinu-a-okrasne-zahradnictvi",
        "props": {"ICO": "00027073", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04gf11d56",
            "URL": "http://www.vukoz.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav Silva Taroucy pro krajinu a okrasné zahradnictví",
            "en": "Silva Tarouca Research Institute for Landscape and Ornamental Gardening",
        },
    },
    {
        "id": "vyzkumny-ustav-vodohospodarsky-t-g-masaryka",
        "props": {"ICO": "00020711", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0582kjx49",
            "URL": "https://www.vuv.cz/index.php/cz/",
        },
        "title": {
            "cs": "Výzkumný ústav vodohospodářský T. G. Masaryka",
            "en": "T. G. Masaryk Water Research Institute",
        },
    },
    {
        "id": "amu",
        "props": {"ICO": "61384984", "acronym": "AMU", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/05mjwh489", "URL": "http://www.amu.cz"},
        "title": {
            "cs": "Akademie múzických umění v Praze",
            "en": "Academy of Performing Arts in Prague",
        },
    },
    {
        "id": "avu",
        "props": {"ICO": "60461446", "acronym": "AVU", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/04nvnkt69", "URL": "http://www.avu.cz"},
        "title": {
            "cs": "Akademie výtvarných umění v Praze",
            "en": "Academy of Fine Arts in Prague",
        },
    },
    {
        "id": "czu",
        "props": {"ICO": "60460709", "acronym": "ČZU", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/0415vcw02", "URL": "http://czu.cz/"},
        "title": {
            "cs": "Česká zemědělská univerzita v Praze",
            "en": "Czech University of Life Sciences Prague",
        },
    },
    {
        "id": "cvut",
        "props": {"ICO": "68407700", "acronym": "ČVUT", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/03kqpb082", "URL": "http://www.cvut.cz"},
        "title": {
            "cs": "České vysoké učení technické v Praze",
            "en": "Czech Technical University in Prague",
        },
    },
    {
        "id": "jamu",
        "props": {"ICO": "62156462", "acronym": "JAMU", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/01n7dqn92", "URL": "http://www.jamu.cz"},
        "title": {
            "cs": "Janáčkova akademie múzických umění v Brně",
            "en": "Janáček Academy of Music and Performing Arts in Brno",
        },
    },
    {
        "id": "jcu",
        "props": {"ICO": "60076658", "acronym": "JČU", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/033n3pw66", "URL": "http://www.jcu.cz"},
        "title": {
            "cs": "Jihočeská univerzita v Českých Budějovicích",
            "en": "University of South Bohemia in České Budějovice",
        },
    },
    {
        "id": "mu",
        "props": {"ICO": "00216224", "acronym": "MU", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02j46qs45", "URL": "http://www.muni.cz"},
        "title": {"cs": "Masarykova univerzita", "en": "Masaryk University"},
    },
    {
        "id": "mendelu",
        "nonpreferredLabels": [
            {"cs": "Mendelova univerzita"},
            {"cs": "Mendelova zemědělská a lesnická univerzita"},
            {"cs": "Mendelova univerzita (Brno)"},
            {"cs": "Vysoká škola zemědělská a lesnická v Brně"},
            {"cs": "Vysoká škola zemědělská v Brně"},
            {"cs": "Mendelova zemědělská a lesnická univerzita v Brně"},
        ],
        "props": {
            "ICO": "62156489",
            "acronym": "MENDELU",
            "nameType": "organizational",
        },
        "relatedURI": {
            "ROR": "https://ror.org/058aeep47",
            "URL": "http://www.mendelu.cz",
        },
        "title": {
            "cs": "Mendelova univerzita v Brně",
            "en": "Mendel University in Brno",
        },
    },
    {
        "id": "ostravska-univerzita",
        "props": {"ICO": "61988987", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/00pyqav47", "URL": "http://www.osu.cz"},
        "title": {"cs": "Ostravská univerzita", "en": "University of Ostrava"},
    },
    {
        "id": "slezska-univerzita-v-opave",
        "props": {"ICO": "47813059", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02w4f2z17", "URL": "http://www.slu.cz"},
        "title": {
            "cs": "Slezská univerzita v Opavě",
            "en": "Silesian University in Opava",
        },
    },
    {
        "id": "tul",
        "props": {"ICO": "46747885", "acronym": "TUL", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02jtk7k02", "URL": "http://www.tul.cz"},
        "title": {
            "cs": "Technická univerzita v Liberci",
            "en": "Technical University of Liberec",
        },
    },
    {
        "id": "univerzita-hradec-kralove",
        "props": {"ICO": "62690094", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/05k238v14", "URL": "http://www.uhk.cz"},
        "title": {
            "cs": "Univerzita Hradec Králové",
            "en": "University of Hradec Králové",
        },
    },
    {
        "id": "ujep",
        "props": {"ICO": "44555601", "acronym": "UJEP", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/04vjwcp92", "URL": "http://www.ujep.cz"},
        "title": {
            "cs": "Univerzita Jana Evangelisty Purkyně v Ústí nad Labem",
            "en": "Jan Evangelista Purkyně University in Ústí nad Labem",
        },
    },
    {
        "id": "uk",
        "props": {"ICO": "00216208", "acronym": "UK", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/024d6js02", "URL": "http://www.cuni.cz"},
        "title": {"cs": "Univerzita Karlova", "en": "Charles University"},
    },
    {
        "id": "univerzita-palackeho-v-olomouci",
        "props": {"ICO": "61989592", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/04qxnmv42", "URL": "http://www.upol.cz"},
        "title": {
            "cs": "Univerzita Palackého v Olomouci",
            "en": "Palacký University Olomouc",
        },
    },
    {
        "id": "upce",
        "props": {"ICO": "00216275", "acronym": "UPCE", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/01chzd453", "URL": "http://www.upce.cz"},
        "title": {"cs": "Univerzita Pardubice", "en": "University of Pardubice"},
    },
    {
        "id": "utb",
        "props": {"ICO": "70883521", "acronym": "UTB", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/04nayfw11", "URL": "http://www.utb.cz"},
        "title": {
            "cs": "Univerzita Tomáše Bati ve Zlíně",
            "en": "Tomas Bata University in Zlín",
        },
    },
    {
        "id": "vfu",
        "props": {"ICO": "62157124", "acronym": "VFU", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/04rk6w354", "URL": "http://www.vfu.cz"},
        "title": {
            "cs": "Veterinární a farmaceutická univerzita Brno",
            "en": "University of Veterinary and Pharmaceutical Sciences Brno",
        },
    },
    {
        "id": "vsb-tuo",
        "props": {
            "ICO": "61989100",
            "acronym": "VŠB-TUO",
            "nameType": "organizational",
        },
        "relatedURI": {"ROR": "https://ror.org/05x8mcb75", "URL": "http://www.vsb.cz"},
        "title": {
            "cs": "Vysoká škola báňská - Technická univerzita Ostrava",
            "en": "VSB - Technical University of Ostrava",
        },
    },
    {
        "id": "vse",
        "nonpreferredLabels": [{"en": "University of Economics, Prague"}],
        "props": {"ICO": "61384399", "acronym": "VŠE", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/029ecwj92", "URL": "http://www.vse.cz"},
        "title": {
            "cs": "Vysoká škola ekonomická v Praze",
            "en": "Prague University of Economics and Business",
        },
    },
    {
        "id": "vscht",
        "props": {"ICO": "60461373", "acronym": "VŠCHT", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05ggn0a85",
            "URL": "http://www.vscht.cz",
        },
        "title": {
            "cs": "Vysoká škola chemicko-technologická v Praze",
            "en": "University of Chemistry and Technology, Prague",
        },
    },
    {
        "id": "vysoka-skola-polytechnicka-jihlava",
        "props": {"ICO": "71226401", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/05c4w7j07", "URL": "http://www.vspj.cz"},
        "title": {
            "cs": "Vysoká škola polytechnická Jihlava",
            "en": "College of Polytechnics Jihlava",
        },
    },
    {
        "id": "vysoka-skola-technicka-a-ekonomicka-v-ceskych-budejovicich",
        "props": {"ICO": "75081431", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05a70k539",
            "URL": "http://www.vstecb.cz",
        },
        "title": {
            "cs": "Vysoká škola technická a ekonomická v Českých Budějovicích",
            "en": "Institute of Technology and Business in České Budějovice",
        },
    },
    {
        "id": "umprum",
        "props": {"ICO": "60461071", "acronym": "UMPRUM", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02ea0g317", "URL": "http://www.vsup.cz"},
        "title": {
            "cs": "Vysoká škola uměleckoprůmyslová v Praze",
            "en": "Academy of Arts, Architecture and Design in Prague",
        },
    },
    {
        "id": "vut",
        "props": {"ICO": "00216305", "acronym": "VUT", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03613d656",
            "URL": "http://www.vutbr.cz",
        },
        "title": {
            "cs": "Vysoké učení technické v Brně",
            "en": "Brno University of Technology",
        },
    },
    {
        "id": "zcu",
        "props": {"ICO": "49777513", "acronym": "ZČU", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/040t43x18", "URL": "http://www.zcu.cz"},
        "title": {
            "cs": "Západočeská univerzita v Plzni",
            "en": "University of West Bohemia",
        },
    },
    {
        "id": "policejni-akademie-ceske-republiky-v-praze",
        "props": {"ICO": "48135445", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02h92td50",
            "URL": "http://www.polac.cz",
        },
        "title": {
            "cs": "Policejní akademie České republiky v Praze",
            "en": "Police Academy of the Czech Republic in Prague",
        },
    },
    {
        "id": "univerzita-obrany",
        "props": {"ICO": "60162694", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/04arkmn57", "URL": "http://www.unob.cz"},
        "title": {"cs": "Univerzita obrany", "en": "University of Defence in Brno"},
    },
    {
        "id": "cenia-ceska-informacni-agentura-zivotniho-prostredi",
        "props": {"ICO": "45249130", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00xh22n12",
            "URL": "http://www.cenia.cz",
        },
        "title": {
            "cs": "CENIA, česká informační agentura životního prostředí",
            "en": "CENIA",
        },
    },
    {
        "id": "centrum-pro-regionalni-rozvoj-ceske-republiky",
        "props": {"ICO": "04095316", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/031ytbr64", "URL": "http://www.crr.cz"},
        "title": {
            "cs": "Centrum pro regionální rozvoj České republiky",
            "en": "Centre for Regional Development of the Czech Republic",
        },
    },
    {
        "id": "csu",
        "props": {"ICO": "00025593", "acronym": "ČSÚ", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03w948j83",
            "URL": "https://www.czso.cz/",
        },
        "title": {"cs": "Český statistický úřad", "en": "Czech Statistical Office"},
    },
    {
        "id": "ministerstvo-obrany-cr",
        "props": {"ICO": "60162694", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00r7raa16",
            "URL": "https://www.army.cz/",
        },
        "title": {
            "cs": "Ministerstvo obrany ČR",
            "en": "Ministry of Defence of the Czech Republic",
        },
    },
    {
        "id": "ministerstvo-spravedlnosti-cr",
        "props": {"ICO": "00025429", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0531qh590",
            "URL": "https://portal.justice.cz",
        },
        "title": {
            "cs": "Ministerstvo spravedlnosti ČR",
            "en": "Ministry of Justice of the Czech Republic",
        },
    },
    {
        "id": "ministerstvo-zivotniho-prostredi-cr",
        "props": {"ICO": "00164801", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04e74dh47",
            "URL": "https://www.mzp.cz/",
        },
        "title": {
            "cs": "Ministerstvo životního prostředí ČR",
            "en": "Ministry of the Environment of the Czech Republic",
        },
    },
    {
        "id": "nuv",
        "props": {"ICO": "00022179", "acronym": "NÚV", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/03enrvz51", "URL": "http://www.nuv.cz"},
        "title": {
            "cs": "Národní ústav pro vzdělávání",
            "en": "National Institute for Education",
        },
    },
    {
        "id": "pi",
        "props": {"acronym": "PI", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00zahx847",
            "URL": "http://www.psp.cz/sqw/hp.sqw?k=40",
        },
        "title": {"cs": "Parlamentní institut", "en": "Parliamentary Institute"},
    },
    {
        "id": "surao",
        "props": {"ICO": "66000769", "acronym": "SÚRAO", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05pa5kt82",
            "URL": "http://www.surao.cz/",
        },
        "title": {
            "cs": "Správa úložišť radioaktivních odpadů",
            "en": "Czech Radioactive Waste Repository Authority",
        },
    },
    {
        "id": "szpi",
        "props": {"ICO": "75014149", "acronym": "SZPI", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05yjswp61",
            "URL": "http://www.szpi.gov.cz",
        },
        "title": {
            "cs": "Státní zemědělská a potravinářská inspekce",
            "en": "Czech Agriculture and Food Inspection Authority",
        },
    },
    {
        "id": "upv",
        "props": {"ICO": "48135097", "acronym": "ÚPV", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/05tp92v87", "URL": "http://upv.cz/"},
        "title": {
            "cs": "Úřad průmyslového vlastnictví",
            "en": "Industrial Property Office",
        },
    },
    {
        "id": "archip",
        "props": {"ICO": "28881699", "acronym": "Archip", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0286btk29",
            "URL": "http://www.archip.eu",
        },
        "title": {
            "cs": "Architectural Institute in Prague",
            "en": "Architectural Institute in Prague",
        },
    },
    {
        "id": "prague-college",
        "props": {"ICO": "27164004", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01x9n3j10",
            "URL": "http://www.praguecollege.cz/",
        },
        "tags": ["deprecated"],
        "title": {"cs": "Prague College"},
    },
    {
        "id": "vsers",
        "props": {"ICO": "26033909", "acronym": "VŠERS", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/040qrz805",
            "URL": "http://www.vsers.cz",
        },
        "title": {
            "cs": "Vysoká škola evropských a regionálních studií",
            "en": "College of European and Regional Studies",
        },
    },
    {
        "id": "vysoka-skola-financni-a-spravni",
        "props": {"ICO": "04274644", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/020ydms54", "URL": "http://www.vsfs.cz"},
        "title": {
            "cs": "Vysoká škola finanční a správní",
            "en": "University of Finance and Administration",
        },
    },
    {
        "id": "vysoka-skola-podnikani-a-prava",
        "nonpreferredLabels": [
            {"cs": "Vysoká škola manažerské informatiky a ekonomiky"}
        ],
        "props": {"ICO": "04130081", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/016emmf09", "URL": "http://www.vspp.cz"},
        "tags": ["deprecated"],
        "title": {
            "cs": "Vysoká škola podnikání a práva",
            "en": "College of Entrepreneurship and Law",
        },
    },
    {
        "id": "osobni-archiv-doc-rndr-jiriho-souceka-drsc-",
        "props": {"nameType": "organizational"},
        "title": {
            "cs": "Osobní archiv doc. RNDr. Jiřího Součka, DrSc.",
            "en": "Personal archive of Jiří Souček",
        },
    },
    {
        "id": "osobni-archiv-ing-arch-jana-moucky",
        "props": {"nameType": "organizational"},
        "title": {
            "cs": "Osobní archiv Ing. arch. Jana Moučky",
            "en": "Personal archive of Jan Moučka",
        },
    },
    {
        "id": "arnika",
        "props": {"ICO": "26543281", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/05dxd7816", "URL": "http://arnika.org/"},
        "title": {"cs": "Arnika", "en": "Arnika"},
    },
    {
        "id": "centrum-pro-dopravu-a-energetiku",
        "props": {"ICO": "67980961", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/002jrdr94",
            "URL": "https://cde.ecn.cz/",
        },
        "title": {
            "cs": "Centrum pro dopravu a energetiku",
            "en": "Centre for Transport and Energy",
        },
    },
    {
        "id": "ceska-asociace-ergoterapeutu",
        "props": {"ICO": "62348451", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05t43a661",
            "URL": "http://ergoterapie.cz/",
        },
        "title": {
            "cs": "Česká asociace ergoterapeutů",
            "en": "Czech Association of Occupational Therapists",
        },
    },
    {
        "id": "czepa",
        "props": {"ICO": "00473146", "acronym": "CZEPA", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00csdcr36",
            "URL": "http://www.czepa.cz/",
        },
        "title": {
            "cs": "Česká asociace paraplegiků",
            "en": "Czech Paraplegics Association",
        },
    },
    {
        "id": "crdm",
        "props": {"ICO": "68379439", "acronym": "ČRDM", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/00qzqdm10", "URL": "http://crdm.cz/"},
        "title": {
            "cs": "Česká rada dětí a mládeže",
            "en": "Czech Council of Children and Youth",
        },
    },
    {
        "id": "ceska-spolecnost-ornitologicka",
        "props": {"ICO": "49629549", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/054stgg72",
            "URL": "http://www.birdlife.cz/",
        },
        "title": {
            "cs": "Česká společnost ornitologická",
            "en": "Czech Society for Ornithology",
        },
    },
    {
        "id": "clovek-v-tisni",
        "props": {"ICO": "25755277", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00kr65d46",
            "URL": "http://www.clovekvtisni.cz",
        },
        "title": {"cs": "Člověk v tísni", "en": "People in Need Czech Republic"},
    },
    {
        "id": "ekodomov",
        "props": {"ICO": "26664488", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0301hkr79",
            "URL": "http://www.ekodomov.cz/",
        },
        "title": {"cs": "Ekodomov", "en": "Ekodomov"},
    },
    {
        "id": "evropske-hodnoty",
        "props": {"ICO": "26987627", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/031xfkk69",
            "URL": "http://www.evropskehodnoty.cz/",
        },
        "title": {"cs": "Evropské hodnoty", "en": "European Values"},
    },
    {
        "id": "fairtrade-cesko-a-slovensko",
        "props": {"ICO": "71226672", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01nr4vy20",
            "URL": "https://www.fairtrade-cesko.cz",
        },
        "title": {
            "cs": "Fairtrade Česko a Slovensko",
            "en": "Fairtrade Czech Republic & Slovakia",
        },
    },
    {
        "id": "gender-studies",
        "props": {"ICO": "25737058", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00at2pp81",
            "URL": "http://www.genderstudies.cz/",
        },
        "title": {"cs": "Gender Studies", "en": "Gender Studies"},
    },
    {
        "id": "gle",
        "props": {"ICO": "28204409", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/005nzs995", "URL": "http://gle.cz/"},
        "title": {"cs": "GLE", "en": "GLE"},
    },
    {
        "id": "hestia",
        "props": {"ICO": "67779751", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05xeax323",
            "URL": "http://www.hest.cz/",
        },
        "title": {"cs": "HESTIA", "en": "HESTIA"},
    },
    {
        "id": "iure",
        "props": {"ICO": "26534487", "acronym": "IURE", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/049kbyp41",
            "URL": "http://www.iure.org/",
        },
        "title": {"cs": "Iuridicum Remedium"},
    },
    {
        "id": "nadace-promeny-karla-komarka",
        "nonpreferredLabels": [
            {"cs": "Nadace Proměny"},
            {"cs": "Nadace Proměny Karla Komárka"},
            {"en": "Karel Komárek Proměny Foundation"},
        ],
        "props": {"ICO": "27421538", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02rs6vz87",
            "URL": "http://www.nadace-promeny.cz/",
        },
        "title": {
            "cs": "Nadace Karel Komárek Family Foundation",
            "en": "Karel Komárek Family Foundation",
        },
    },
    {
        "id": "simi",
        "props": {"ICO": "26612933", "acronym": "SIMI", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00y2q5g68",
            "URL": "http://www.migrace.com/",
        },
        "title": {
            "cs": "Sdružení pro integraci a migraci",
            "en": "Association for Integration and Migration",
        },
    },
    {
        "id": "siriri",
        "props": {"ICO": "27447669", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03adnqh21",
            "URL": "https://siriri.org/",
        },
        "title": {"cs": "SIRIRI", "en": "SIRIRI"},
    },
    {
        "id": "jihomoravske-muzeum-ve-znojme",
        "props": {"ICO": "00092738", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/006eggh59",
            "URL": "http://www.znojmuz.cz/",
        },
        "title": {
            "cs": "Jihomoravské muzeum ve Znojmě",
            "en": "South Moravian Museum in Znojmo",
        },
    },
    {
        "id": "muzeum-brnenska",
        "props": {"ICO": "00089257", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03nc1mn84",
            "URL": "https://www.muzeumbrnenska.cz",
        },
        "title": {"cs": "Muzeum Brněnska", "en": "Museum of the Brno Region"},
    },
    {
        "id": "muzeum-vychodnich-cech-v-hradci-kralove",
        "props": {"ICO": "00088382", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01x1xh678",
            "URL": "http://www.muzeumhk.cz",
        },
        "title": {
            "cs": "Muzeum východních Čech v Hradci Králové",
            "en": "East Bohemian Museum in Hradec Králové",
        },
    },
    {
        "id": "narodni-muzeum",
        "props": {"ICO": "00023272", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/04z6gwv56", "URL": "http://www.nm.cz/"},
        "title": {"cs": "Národní muzeum", "en": "National Museum"},
    },
    {
        "id": "narodni-muzeum-v-prirode",
        "props": {"ICO": "00098604", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03sxmek83",
            "URL": "https://www.nmvp.cz/",
        },
        "title": {"cs": "Národní muzeum v přírodě", "en": "National Open-Air Museum"},
    },
    {
        "id": "ntm",
        "props": {"ICO": "00023299", "acronym": "NTM", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02fy0zn70", "URL": "http://www.ntm.cz/"},
        "title": {"cs": "Národní technické muzeum", "en": "National Technical Museum"},
    },
    {
        "id": "narodni-zemedelske-muzeum",
        "props": {"ICO": "75075741", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/04a98ab79", "URL": "http://nzm.cz/"},
        "title": {
            "cs": "Národní zemědělské muzeum",
            "en": "National Museum of Agriculture",
        },
    },
    {
        "id": "pnp",
        "props": {"ICO": "00023311", "acronym": "PNP", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05teadr95",
            "URL": "http://www.pamatniknarodnihopisemnictvi.cz/",
        },
        "title": {
            "cs": "Památník národního písemnictví",
            "en": "Museum of Czech Literature",
        },
    },
    {
        "id": "severoceske-muzeum-v-liberci",
        "props": {"ICO": "00083232", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/009ps8477",
            "URL": "http://www.muzeumlb.cz/",
        },
        "title": {
            "cs": "Severočeské muzeum v Liberci",
            "en": "North Bohemian Museum in Liberec",
        },
    },
    {
        "id": "slezske-zemske-muzeum",
        "props": {"ICO": "00100595", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/0404wkz93", "URL": "http://www.szm.cz/"},
        "title": {"cs": "Slezské zemské muzeum", "en": "Silesian Museum"},
    },
    {
        "id": "upm",
        "props": {"ICO": "00023442", "acronym": "UPM", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02y7mzf89", "URL": "http://www.upm.cz/"},
        "title": {
            "cs": "Uměleckoprůmyslové museum",
            "en": "Museum of Decorative Arts in Prague",
        },
    },
    {
        "id": "zcm",
        "props": {"ICO": "00228745", "acronym": "ZČM", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/016jp5513", "URL": "http://www.zcm.cz/"},
        "title": {
            "cs": "Západočeské muzeum v Plzni",
            "en": "Museum of West Bohemia in Pilsen",
        },
    },
    {
        "id": "knav",
        "props": {"ICO": "67985971", "acronym": "KNAV", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/028sgmw18",
            "URL": "http://www.lib.cas.cz/",
        },
        "title": {
            "cs": "Knihovna AV ČR",
            "en": "Library of the Czech Academy of Sciences",
        },
    },
    {
        "id": "mzk",
        "props": {"ICO": "00094943", "acronym": "MZK", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/03f239z63", "URL": "http://www.mzk.cz/"},
        "title": {"cs": "Moravská zemská knihovna", "en": "Moravian Library"},
    },
    {
        "id": "nk cr",
        "props": {"ICO": "00023221", "acronym": "NK ČR", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/038agj363",
            "URL": "https://www.nkp.cz/",
        },
        "title": {
            "cs": "Národní knihovna ČR",
            "en": "National Library of the Czech Republic",
        },
    },
    {
        "id": "nlk",
        "props": {"ICO": "00023825", "acronym": "NLK", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/03zszgs95", "URL": "http://www.nlk.cz/"},
        "title": {"cs": "Národní lékařská knihovna", "en": "National Medical Library"},
    },
    {
        "id": "ntk",
        "props": {"ICO": "61387142", "acronym": "NTK", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/028txef36", "URL": "http://techlib.cz/"},
        "title": {
            "cs": "Národní technická knihovna",
            "en": "National Library of Technology",
        },
    },
    {
        "id": "gvuo",
        "props": {"ICO": "00373231", "acronym": "GVUO", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04hazwa85",
            "URL": "http://www.gvuo.cz/",
        },
        "title": {
            "cs": "Galerie výtvarného umění v Ostravě",
            "en": "Gallery of Fine Arts in Ostrava",
        },
    },
    {
        "id": "moravska-galerie-v-brne",
        "props": {"ICO": "00094871", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01tkgk805",
            "URL": "http://www.moravska-galerie.cz/",
        },
        "title": {"cs": "Moravská galerie v Brně", "en": "Moravian Gallery in Brno"},
    },
    {
        "id": "arub",
        "props": {"ICO": "68081758", "acronym": "ARÚB", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02bvcjw39",
            "URL": "http://www.arub.cz/",
        },
        "title": {
            "cs": "Archeologický ústav AV ČR, Brno",
            "en": "Institute of Archaeology of the CAS, Brno",
        },
    },
    {
        "id": "archeologicky-ustav-av-cr-praha",
        "props": {"ICO": "67985912", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0287jta43",
            "URL": "http://www.arup.cas.cz/",
        },
        "title": {
            "cs": "Archeologický ústav AV ČR, Praha",
            "en": "Institute of Archaeology of the CAS, Prague",
        },
    },
    {
        "id": "astronomicky-ustav-av-cr",
        "props": {"ICO": "67985815", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03tp8z347",
            "URL": "http://www.asu.cas.cz/",
        },
        "title": {
            "cs": "Astronomický ústav AV ČR",
            "en": "Astronomical Institute of the CAS",
        },
    },
    {
        "id": "biofyzikalni-ustav-av-cr",
        "props": {"ICO": "68081707", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/00angvn73", "URL": "http://www.ibp.cz/"},
        "title": {
            "cs": "Biofyzikální ústav AV ČR",
            "en": "Institute of Biophysics of the CAS",
        },
    },
    {
        "id": "biologicke-centrum-av-cr",
        "props": {"ICO": "60077344", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05pq4yn02",
            "URL": "http://www.bc.cas.cz/",
        },
        "title": {"cs": "Biologické centrum AV ČR", "en": "Biology Centre of the CAS"},
    },
    {
        "id": "biotechnologicky-ustav-av-cr",
        "props": {"ICO": "86652036", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00wzqmx94",
            "URL": "http://www.ibt.cas.cz/cs",
        },
        "title": {
            "cs": "Biotechnologický ústav AV ČR",
            "en": "Institute of Biotechnology of the CAS",
        },
    },
    {
        "id": "botanicky-ustav-av-cr",
        "props": {"ICO": "67985939", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03qqnc658",
            "URL": "http://www.ibot.cas.cz/",
        },
        "title": {
            "cs": "Botanický ústav AV ČR",
            "en": "Institute of Botany of the CAS",
        },
    },
    {
        "id": "sociologicky-ustav-av-cr",
        "props": {"ICO": "68378025", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/018hy5194",
            "URL": "http://www.soc.cas.cz/",
        },
        "title": {
            "cs": "Sociologický ústav AV ČR",
            "en": "Institute of Sociology of the CAS",
        },
    },
    {
        "id": "entomologicky-ustav-av-cr",
        "props": {"nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/039nazg33",
            "URL": "http://www.entu.cas.cz/",
        },
        "tags": ["deprecated"],
        "title": {
            "cs": "Entomologický ústav AV ČR",
            "en": "Institute of Entomology of the CAS",
        },
    },
    {
        "id": "etnologicky-ustav-av-cr",
        "props": {"ICO": "68378076", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01qj7sc02",
            "URL": "http://www.eu.cas.cz/",
        },
        "title": {
            "cs": "Etnologický ústav AV ČR",
            "en": "Institute of Ethnology of the CAS",
        },
    },
    {
        "id": "filosoficky-ustav-av-cr",
        "props": {"ICO": "67985955", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01hyg6578",
            "URL": "http://www.flu.cas.cz",
        },
        "title": {
            "cs": "Filosofický ústav AV ČR",
            "en": "Institute of Philosophy of the CAS",
        },
    },
    {
        "id": "fyzikalni-ustav-av-cr",
        "props": {"ICO": "68378271", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02yhj4v17", "URL": "http://www.fzu.cz/"},
        "title": {
            "cs": "Fyzikální ústav AV ČR",
            "en": "Institute of Physics of the CAS",
        },
    },
    {
        "id": "fyziologicky-ustav-av-cr",
        "props": {"ICO": "67985823", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05xw0ep96",
            "URL": "http://www.fgu.cas.cz/",
        },
        "title": {
            "cs": "Fyziologický ústav AV ČR",
            "en": "Institute of Physiology of the CAS",
        },
    },
    {
        "id": "geofyzikalni-ustav-av-cr",
        "props": {"ICO": "67985530", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02e8b2r87",
            "URL": "http://www.ig.cas.cz/",
        },
        "title": {
            "cs": "Geofyzikální ústav AV ČR",
            "en": "Institute of Geophysics of the CAS",
        },
    },
    {
        "id": "geologicky-ustav-av-cr",
        "props": {"ICO": "67985831", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04wh80b80",
            "URL": "http://www.gli.cas.cz",
        },
        "title": {
            "cs": "Geologický ústav AV ČR",
            "en": "Institute of Geology of the CAS",
        },
    },
    {
        "id": "historicky-ustav-av-cr",
        "props": {"ICO": "67985963", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03tybc759",
            "URL": "http://www.hiu.cas.cz/",
        },
        "title": {
            "cs": "Historický ústav AV ČR",
            "en": "Institute of History of the CAS",
        },
    },
    {
        "id": "hydrobiologicky-ustav-av-cr",
        "props": {"nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0436nxt45",
            "URL": "http://www.hbu.cas.cz",
        },
        "tags": ["deprecated"],
        "title": {
            "cs": "Hydrobiologický ústav AV ČR",
            "en": "Institute of Hydrobiology of the CAS",
        },
    },
    {
        "id": "masarykuv-ustav-a-archiv-av-cr",
        "props": {"ICO": "67985921", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03nvfe914",
            "URL": "http://www.mua.cas.cz",
        },
        "title": {
            "cs": "Masarykův ústav a Archiv AV ČR",
            "en": "Masaryk Institute and Archives of the CAS",
        },
    },
    {
        "id": "matematicky-ustav-av-cr",
        "props": {"ICO": "67985840", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02tv1yf50",
            "URL": "http://www.math.cas.cz",
        },
        "title": {
            "cs": "Matematický ústav AV ČR",
            "en": "Institute of Mathematics of the CAS",
        },
    },
    {
        "id": "mikrobiologicky-ustav-av-cr",
        "props": {"ICO": "61388971", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02p1jz666",
            "URL": "http://www.biomed.cas.cz/mbu/cz/",
        },
        "title": {
            "cs": "Mikrobiologický ústav AV ČR",
            "en": "Institute of Microbiology of the CAS",
        },
    },
    {
        "id": "narodohospodarsky-ustav-av-cr",
        "props": {"ICO": "67985998", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01y3ft232",
            "URL": "http://www.ei.cas.cz",
        },
        "title": {
            "cs": "Národohospodářský ústav AV ČR",
            "en": "Economics Institute of the CAS",
        },
    },
    {
        "id": "orientalni-ustav-av-cr",
        "props": {"ICO": "68378009", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04tr8pt83",
            "URL": "http://www.orient.cas.cz/",
        },
        "title": {
            "cs": "Orientální ústav AV ČR",
            "en": "Oriental Institute of the CAS",
        },
    },
    {
        "id": "parazitologicky-ustav-av-cr",
        "props": {"nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05rhyza23",
            "URL": "http://www.paru.cas.cz/cs/",
        },
        "tags": ["deprecated"],
        "title": {
            "cs": "Parazitologický ústav AV ČR",
            "en": "Institute of Parasitology of the CAS",
        },
    },
    {
        "id": "psychologicky-ustav-av-cr",
        "props": {"ICO": "68081740", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03aba6h29",
            "URL": "http://www.psu.cas.cz/",
        },
        "title": {
            "cs": "Psychologický ústav AV ČR",
            "en": "Institute of Psychology of the CAS",
        },
    },
    {
        "id": "slovansky-ustav-av-cr",
        "props": {"ICO": "68378017", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03qq0n189",
            "URL": "http://www.slu.cas.cz/",
        },
        "title": {
            "cs": "Slovanský ústav AV ČR",
            "en": "Institute of Slavonic Studies of the CAS",
        },
    },
    {
        "id": "stredisko-spolecnych-cinnosti",
        "props": {"ICO": "60457856", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03zkxs276",
            "URL": "http://www.ssc.cas.cz/cs/",
        },
        "title": {
            "cs": "Středisko společných činností",
            "en": "Centre for Administration and Operations of the ASCR",
        },
    },
    {
        "id": "technologicke-centrum-av-cr",
        "props": {"ICO": "60456540", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02tc3qm58", "URL": "http://www.tc.cz/"},
        "title": {
            "cs": "Technologické centrum AV ČR",
            "en": "Technology Centre of the CAS",
        },
    },
    {
        "id": "ustav-analyticke-chemie-av-cr",
        "props": {"ICO": "68081715", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05g7knd32",
            "URL": "http://www.iach.cz/",
        },
        "title": {
            "cs": "Ústav analytické chemie AV ČR",
            "en": "Institute of Analytical Chemistry of the CAS",
        },
    },
    {
        "id": "ustav-anorganicke-chemie-av-cr",
        "props": {"ICO": "61388980", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01hsjcv06",
            "URL": "http://www.iic.cas.cz/",
        },
        "title": {
            "cs": "Ústav anorganické chemie AV ČR",
            "en": "Institute of Inorganic Chemistry of the CAS",
        },
    },
    {
        "id": "ustav-biologie-obratlovcu-av-cr",
        "props": {"ICO": "68081766", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/05bcgdd94", "URL": "http://www.ivb.cz"},
        "title": {
            "cs": "Ústav biologie obratlovců AV ČR",
            "en": "Institute of Vertebrate Biology of the CAS",
        },
    },
    {
        "id": "ustav-dejin-umeni-av-cr",
        "props": {"ICO": "68378033", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00913gw18",
            "URL": "http://www.udu.cas.cz/",
        },
        "title": {
            "cs": "Ústav dějin umění AV ČR",
            "en": "Institute of Art History of the CAS",
        },
    },
    {
        "id": "ustav-experimentalni-botaniky-av-cr",
        "props": {"ICO": "61389030", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/057br4398",
            "URL": "http://www.ueb.cas.cz/",
        },
        "title": {
            "cs": "Ústav experimentální botaniky AV ČR",
            "en": "Institute of Experimental Botany of the CAS",
        },
    },
    {
        "id": "ustav-experimentalni-mediciny-av-cr",
        "props": {"ICO": "68378041", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03hjekm25",
            "URL": "http://www.iem.cas.cz/",
        },
        "title": {
            "cs": "Ústav experimentální medicíny AV ČR",
            "en": "Institute of Experimental Medicine of the CAS",
        },
    },
    {
        "id": "ustav-fotoniky-a-elektroniky-av-cr",
        "props": {"ICO": "67985882", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/05wrbcx33", "URL": "http://www.ufe.cz/"},
        "title": {
            "cs": "Ústav fotoniky a elektroniky AV ČR",
            "en": "Institute of Photonics and Electronics of the CAS",
        },
    },
    {
        "id": "ustav-fyzikalni-chemie-j-heyrovskeho-av-cr",
        "props": {"ICO": "61388955", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02sat5y74",
            "URL": "http://www.jh-inst.cas.cz/",
        },
        "title": {
            "cs": "Ústav fyzikální chemie J. Heyrovského AV ČR",
            "en": "J. Heyrovsky Institute of Physical Chemistry of the CAS",
        },
    },
    {
        "id": "ustav-fyziky-atmosfery-av-cr",
        "props": {"ICO": "68378289", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04vtzcr32",
            "URL": "http://www.ufa.cas.cz/",
        },
        "title": {
            "cs": "Ústav fyziky atmosféry AV ČR",
            "en": "Institute of Atmospheric Physics  of the CAS",
        },
    },
    {
        "id": "ustav-fyziky-materialu-av-cr",
        "props": {"ICO": "68081723", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02d02f052", "URL": "http://www.ipm.cz/"},
        "title": {
            "cs": "Ústav fyziky materiálů AV ČR",
            "en": "Institute of Physics of Materials of the CAS",
        },
    },
    {
        "id": "ustav-fyziky-plazmatu-av-cr",
        "props": {"ICO": "61389021", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01h494015",
            "URL": "http://www.ipp.cas.cz/",
        },
        "title": {
            "cs": "Ústav fyziky plazmatu AV ČR",
            "en": "Institute of Plasma Physics of the CAS",
        },
    },
    {
        "id": "ustav-geoniky-av-cr",
        "props": {"ICO": "68145535", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02d3n7h84",
            "URL": "http://www.ugn.cas.cz/",
        },
        "title": {"cs": "Ústav geoniky AV ČR", "en": "Institute of Geonics of the CAS"},
    },
    {
        "id": "ustav-chemickych-procesu-av-cr",
        "props": {"ICO": "67985858", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02acv3g39",
            "URL": "http://www.icpf.cas.cz/",
        },
        "title": {
            "cs": "Ústav chemických procesů AV ČR",
            "en": "Institute of Chemical Process Fundamentals of the CAS",
        },
    },
    {
        "id": "ustav-informatiky-av-cr",
        "props": {"ICO": "67985807", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0496n6574",
            "URL": "http://www.cs.cas.cz/",
        },
        "title": {
            "cs": "Ústav informatiky AV ČR",
            "en": "Institute of Computer Science of the CAS",
        },
    },
    {
        "id": "ustav-jaderne-fyziky-av-cr",
        "props": {"ICO": "61389005", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04jymbd90",
            "URL": "http://www.ujf.cas.cz/",
        },
        "title": {
            "cs": "Ústav jaderné fyziky AV ČR",
            "en": "Nuclear Physics Institute of the CAS",
        },
    },
    {
        "id": "ustav-makromolekularni-chemie-av-cr",
        "props": {"ICO": "61389013", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0143w7709",
            "URL": "http://www.imc.cas.cz/",
        },
        "title": {
            "cs": "Ústav makromolekulární chemie AV ČR",
            "en": "Institute of Macromolecular Chemistry of the CAS",
        },
    },
    {
        "id": "ustav-molekularni-biologie-rostlin-av-cr",
        "props": {"nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00jr65m43",
            "URL": "http://www.bc.cas.cz/",
        },
        "tags": ["deprecated"],
        "title": {
            "cs": "Ústav molekulární biologie rostlin AV ČR",
            "en": "Institute of Plant Molecular Biology of the CAS",
        },
    },
    {
        "id": "ustav-molekularni-genetiky-av-cr",
        "props": {"ICO": "68378050", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/045syc608",
            "URL": "http://www.img.cas.cz/",
        },
        "title": {
            "cs": "Ústav molekulární genetiky AV ČR",
            "en": "Institute of Molecular Genetics of the CAS",
        },
    },
    {
        "id": "ustav-organicke-chemie-a-biochemie-av-cr",
        "props": {"ICO": "61388963", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04nfjn472",
            "URL": "http://www.uochb.cz/",
        },
        "title": {
            "cs": "Ústav organické chemie a biochemie AV ČR",
            "en": "Institute of Organic Chemistry and Biochemistry of the CAS",
        },
    },
    {
        "id": "ustav-pro-ceskou-literaturu-av-cr",
        "props": {"ICO": "68378068", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01vr20t27",
            "URL": "http://www.ucl.cas.cz",
        },
        "title": {
            "cs": "Ústav pro českou literaturu AV ČR",
            "en": "Institute of Czech Literature of the CAS",
        },
    },
    {
        "id": "ustav-pro-elektrotechniku",
        "props": {"ICO": "61388998", "nameType": "organizational"},
        "relatedURI": {"URL": "http://www3.it.cas.cz/"},
        "title": {
            "cs": "Ústav pro elektrotechniku",
            "en": "Institute of Electrical Engineering",
        },
    },
    {
        "id": "ustav-pro-hydrodynamiku-av-cr",
        "props": {"ICO": "67985874", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/009wryk55",
            "URL": "http://www.ih.cas.cz/",
        },
        "title": {
            "cs": "Ústav pro hydrodynamiku AV ČR",
            "en": "Institute of Hydrodynamics of the CAS",
        },
    },
    {
        "id": "ustav-pro-jazyk-cesky-av-cr",
        "props": {"ICO": "68378092", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01912nj27",
            "URL": "http://www.ujc.cas.cz/",
        },
        "title": {
            "cs": "Ústav pro jazyk český AV ČR",
            "en": "Czech Language Institute of the CAS",
        },
    },
    {
        "id": "ustav-pro-soudobe-dejiny-av-cr",
        "props": {"ICO": "68378114", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01zghvr36",
            "URL": "http://www.usd.cas.cz/",
        },
        "title": {
            "cs": "Ústav pro soudobé dějiny AV ČR",
            "en": "Institute of Contemporary History of the CAS",
        },
    },
    {
        "id": "ustav-pristrojove-techniky-av-cr",
        "props": {"ICO": "68081731", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/027taah18",
            "URL": "http://www.isibrno.cz/",
        },
        "title": {
            "cs": "Ústav přístrojové techniky AV ČR",
            "en": "Institute of Scientific Instruments of the CAS",
        },
    },
    {
        "id": "ustav-pudni-biologie-av-cr",
        "props": {"nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02tz8r820",
            "URL": "http://www.upb.cas.cz/",
        },
        "tags": ["deprecated"],
        "title": {
            "cs": "Ústav půdní biologie AV ČR",
            "en": "Institute of Soil Biology of the CAS",
        },
    },
    {
        "id": "ustav-statu-a-prava-av-cr",
        "props": {"ICO": "68378122", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00hzy8397",
            "URL": "http://www.ilaw.cas.cz/",
        },
        "title": {
            "cs": "Ústav státu a práva AV ČR",
            "en": "Institute of State and Law of the CAS",
        },
    },
    {
        "id": "ustav-struktury-a-mechaniky-hornin-av-cr",
        "props": {"ICO": "67985891", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00m4pvq34",
            "URL": "http://www.irsm.cas.cz/",
        },
        "title": {
            "cs": "Ústav struktury a mechaniky hornin AV ČR",
            "en": "Institute of Rock Structure and Mechanics of the CAS",
        },
    },
    {
        "id": "ustav-teoreticke-a-aplikovane-mechaniky-av-cr",
        "props": {"ICO": "68378297", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01hxbnq19",
            "URL": "http://www.itam.cas.cz/",
        },
        "title": {
            "cs": "Ústav teoretické a aplikované mechaniky AV ČR",
            "en": "Institute of Theoretical and Applied Mechanics of the CAS",
        },
    },
    {
        "id": "ustav-teorie-informace-a-automatizace-av-cr",
        "props": {"ICO": "67985556", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03h1hsz49",
            "URL": "http://www.utia.cas.cz/",
        },
        "title": {
            "cs": "Ústav teorie informace a automatizace AV ČR",
            "en": "Institute of Information Theory and Automation of the CAS",
        },
    },
    {
        "id": "ustav-termomechaniky-av-cr",
        "props": {"ICO": "61388998", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03fvq2a72",
            "URL": "http://www.it.cas.cz/",
        },
        "title": {
            "cs": "Ústav termomechaniky AV ČR",
            "en": "Institute of Thermomechanics of the CAS",
        },
    },
    {
        "id": "czechglobe",
        "nonpreferredLabels": [{"cs": "Centrum výzkumu globalní změny"}],
        "props": {
            "ICO": "86652079",
            "acronym": "CZECHGLOBE",
            "nameType": "organizational",
        },
        "relatedURI": {
            "ROR": "https://ror.org/01v5hek98",
            "URL": "http://www.czechglobe.cz/",
        },
        "title": {
            "cs": "Ústav výzkumu globální změny AV ČR",
            "en": "Global Change Research Institute of the CAS",
        },
    },
    {
        "id": "ustav-zivocisne-fyziologie-a-genetiky-av-cr",
        "props": {"ICO": "67985904", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0157za327",
            "URL": "http://www.iapg.cas.cz/",
        },
        "title": {
            "cs": "Ústav živočišné fyziologie a genetiky AV ČR",
            "en": "Institute of Animal Physiology and Genetics  of the CAS",
        },
    },
    {
        "id": "narodni-archiv",
        "props": {"ICO": "70979821", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03cykd395",
            "URL": "http://www.nacr.cz/",
        },
        "title": {"cs": "Národní archiv", "en": "National Archives"},
    },
    {
        "id": "cnb",
        "props": {"ICO": "48136450", "acronym": "ČNB", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/05n31vd29", "URL": "http://www.cnb.cz"},
        "title": {"cs": "Česká národní banka", "en": "Czech National Bank"},
    },
    {
        "id": "idu",
        "nonpreferredLabels": [{"cs": "Institut umění - Divadelní ústav"}],
        "props": {"ICO": "00023205", "acronym": "NIPK", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/024jn1h80", "URL": "https://nipk.cz/"},
        "title": {
            "cs": "Národní institut pro kulturu",
            "en": "Czech Cultural Institute",
        },
    },
    {
        "id": "npu",
        "props": {"ICO": "75032333", "acronym": "NPÚ", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/019k25552", "URL": "http://www.npu.cz/"},
        "title": {"cs": "Národní památkový ústav", "en": "National Heritage Institute"},
    },
    {
        "id": "nulk",
        "props": {"ICO": "00094927", "acronym": "NÚLK", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/056kzn313",
            "URL": "http://www.nulk.cz/",
        },
        "title": {
            "cs": "Národní ústav lidové kultury",
            "en": "National Institute of Folk Culture",
        },
    },
    {
        "id": "woodexpert",
        "props": {"ICO": "28282027", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00kygh256",
            "URL": "http://woodexpert.cz/",
        },
        "title": {"cs": "WOODEXPERT"},
    },
    {
        "id": "nfa",
        "props": {"ICO": "00057266", "acronym": "NFA", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/051316d77", "URL": "https://nfa.cz"},
        "title": {"cs": "Národní filmový archiv", "en": "National Film Archive"},
    },
    {
        "id": "czwa",
        "props": {"ICO": "44994397", "acronym": "CzWA", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02m4t4k66",
            "URL": "http://www.czwa.cz/",
        },
        "title": {"cs": "Asociace pro vodu ČR", "en": "Czech Water Association"},
    },
    {
        "id": "ceitec",
        "nonpreferredLabels": [{"cs": "Středoevropský technologický institut"}],
        "props": {"nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01p7k1986",
            "URL": "https://www.ceitec.cz/",
        },
        "title": {"cs": "CEITEC"},
    },
    {
        "id": "aau",
        "props": {"ICO": "25940082", "acronym": "AAU", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03arvv474",
            "URL": "https://www.aauni.edu",
        },
        "title": {
            "cs": "Anglo-American University",
            "en": "Anglo-americká vysoká škola",
        },
    },
    {
        "id": "comtes-fht",
        "props": {"ICO": "26316919", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00hzjtg80",
            "URL": "https://www.comtesfht.cz/",
        },
        "title": {"cs": "COMTES FHT"},
    },
    {
        "id": "statni-oblastni-archiv-v-plzni",
        "props": {"ICO": "70979090", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04753zn39",
            "URL": "http://www.soaplzen.cz/",
        },
        "title": {
            "cs": "Státní oblastní archiv v Plzni",
            "en": "State Regional Archive in Plzeň",
        },
    },
    {
        "id": "mup",
        "props": {"ICO": "26482789", "acronym": "MUP", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01zdaff53",
            "URL": "https://www.mup.cz/",
        },
        "title": {
            "cs": "Metropolitní univerzita Praha",
            "en": "Metropolitan University Prague",
        },
    },
    {
        "id": "npmk",
        "props": {"ICO": "61387169", "acronym": "NPMK", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02fh5m162",
            "URL": "https://www.npmk.cz/",
        },
        "title": {
            "cs": "Národní pedagogické muzeum a knihovna J. A. Komenského",
            "en": "National Pedagogical Museum and Library of J. A. Comenius",
        },
    },
    {
        "id": "nudz",
        "props": {"ICO": "00023752", "acronym": "NUDZ", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05xj56w78",
            "URL": "https://www.nudz.cz",
        },
        "title": {
            "cs": "Národní ústav duševního zdraví",
            "en": "National Institute of Mental Health",
        },
    },
    {
        "id": "nukib",
        "props": {"ICO": "05800226", "acronym": "NÚKIB", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/002wyas44",
            "URL": "https://www.nukib.cz/",
        },
        "title": {
            "cs": "Národní úřad pro kybernetickou a informační bezpečnost",
            "en": "National Cyber and Information Security Agency",
        },
    },
    {
        "id": "suro",
        "props": {"ICO": "86652052", "acronym": "SÚRO", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02vwpg498",
            "URL": "https://www.suro.cz/",
        },
        "title": {
            "cs": "Státní ústav radiační ochrany",
            "en": "National Radiation Protection Institute",
        },
    },
    {
        "id": "savs",
        "props": {"ICO": "29142890", "acronym": "ŠAVŠ", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02zpfcb35",
            "URL": "https://www.savs.cz/",
        },
        "title": {"cs": "ŠKODA AUTO Vysoká škola", "en": "ŠKODA AUTO University"},
    },
    {
        "id": "ta cr",
        "nonpreferredLabels": [{"cs": "TAČR"}, {"en": "TA CR"}],
        "props": {"ICO": "72050365", "acronym": "TA ČR", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04v0fk911",
            "URL": "https://www.tacr.cz",
        },
        "title": {
            "cs": "Technologická agentura České republiky",
            "en": "Technology Agency of the Czech Republic",
        },
    },
    {
        "id": "unyp",
        "props": {"ICO": "25676598", "acronym": "UNYP", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/042hb4t21",
            "URL": "https://www.unyp.cz/cs",
        },
        "title": {"cs": "University of New York in Prague"},
    },
    {
        "id": "ujak",
        "props": {"ICO": "46358978", "acronym": "UJAK", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00ecy3w15",
            "URL": "http://www.ujak.cz/",
        },
        "tags": ["deprecated"],
        "title": {
            "cs": "Univerzita Jana Amose Komenského Praha",
            "en": "Jan Amos Komenský University Prague",
        },
    },
    {
        "id": "umv",
        "props": {"ICO": "48546054", "acronym": "ÚMV", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04hp42s89",
            "URL": "https://www.iir.cz/",
        },
        "title": {
            "cs": "Ústav mezinárodních vztahů",
            "en": "Institute of International Relations Prague",
        },
    },
    {
        "id": "uzei",
        "props": {"ICO": "00027251", "acronym": "ÚZEI", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/042jnea65",
            "URL": "https://www.uzei.cz",
        },
        "title": {
            "cs": "Ústav zemědělské ekonomiky a informací",
            "en": "Institute of Agricultural Economics and Information",
        },
    },
    {
        "id": "vysoka-skola-prigo",
        "props": {"ICO": "25840886", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.vs-prigo.cz"},
        "tags": ["deprecated"],
        "title": {"cs": "Vysoká škola PRIGO", "en": "PRIGO University"},
    },
    {
        "id": "vstvs palestra",
        "props": {
            "ICO": "27132781",
            "acronym": "VŠTVS PALESTRA",
            "nameType": "organizational",
        },
        "relatedURI": {
            "ROR": "https://ror.org/02a5sx544",
            "URL": "https://vstvs.palestra.cz/",
        },
        "title": {
            "cs": "Vysoká škola tělesné výchovy a sportu PALESTRA",
            "en": "College of Physical Education and Sport PALESTRA",
        },
    },
    {
        "id": "cog-cz",
        "nonpreferredLabels": [
            {"cs": "COVID-19 Genomics CZ Consortium"},
            {"en": "COG-CZ - Česká republika"},
        ],
        "props": {"nameType": "organizational"},
        "relatedURI": {"URL": "https://virus.img.cas.cz/"},
        "title": {"cs": "COG-CZ"},
    },
    {
        "id": "fnol",
        "nonpreferredLabels": [{"cs": "FNOL"}],
        "props": {
            "ICO": "00098892",
            "acronym": "FN Olomouc",
            "nameType": "organizational",
        },
        "relatedURI": {
            "ROR": "https://ror.org/01jxtne23",
            "URL": "https://www.fnol.cz/",
        },
        "title": {
            "cs": "Fakultní nemocnice Olomouc",
            "en": "Olomouc University Hospital",
        },
    },
    {
        "id": "fnbrno",
        "props": {
            "ICO": "65269705",
            "acronym": "FN Brno",
            "nameType": "organizational",
        },
        "relatedURI": {
            "ROR": "https://ror.org/00qq1fp34",
            "URL": "https://www.fnbrno.cz/",
        },
        "title": {"cs": "Fakultní nemocnice Brno", "en": "University Hospital Brno"},
    },
    {
        "id": "uni-minnesota",
        "props": {"nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/017zqws13",
            "URL": "https://twin-cities.umn.edu/",
        },
        "title": {"cs": "University of Minnesota", "en": "University of Minnesota"},
    },
    {
        "id": "polytechnique-montreal",
        "props": {"nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05f8d4e86",
            "URL": "https://www.polymtl.ca/",
        },
        "title": {"cs": "Polytechnique Montréal", "en": "Polytechnique Montréal"},
    },
    {
        "id": "cesnet",
        "nonpreferredLabels": [{"cs": "Czech Education and Scientific Network"}],
        "props": {"ICO": "63839172", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/050dkka69",
            "URL": "https://www.cesnet.cz",
        },
        "title": {"cs": "CESNET"},
    },
    {
        "id": "muzeum-skla-a-bizuterie-v-jablonci-nad-nisou",
        "props": {"ICO": "00079481", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.msb-jablonec.cz/novinky"},
        "title": {
            "cs": "Muzeum skla a bižuterie v Jablonci nad Nisou",
            "en": "Museum of Glass and Jewellery",
        },
    },
    {
        "id": "narodni-hrebcin-kladruby-nad-labem",
        "props": {"ICO": "72048972", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05b4e2111",
            "URL": "https://www.nhkladruby.cz/",
        },
        "title": {
            "cs": "Národní hřebčín Kladruby nad Labem",
            "en": "National Stud at Kladruby nad Labem",
        },
    },
    {
        "id": "agrovyzkum-rapotin",
        "props": {"ICO": "26788462", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.vuchs.cz/main/agrovyzkum/"},
        "title": {"cs": "Agrovýzkum Rapotín", "en": "Agrovyzkum Rapotin"},
    },
    {
        "id": "advacam",
        "props": {"ICO": "01732731", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04evkr214",
            "URL": "https://advacam.com",
        },
        "title": {"cs": "ADVACAM", "en": "ADVACAM"},
    },
    {
        "id": "ambis",
        "nonpreferredLabels": [
            {"cs": "Bankovní institut - AMBIS"},
            {"en": "Bankovní institut vysoká škola"},
        ],
        "props": {"ICO": "61858307", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.ambis.cz/"},
        "title": {
            "cs": "AMBIS vysoká škola",
            "en": "College of Regional Development and Banking Institute - AMBIS",
        },
    },
    {
        "id": "centrum-kardiovaskularni-a-transplantacni-chirurgie-brno",
        "props": {"ICO": "00209775", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04adqmv58",
            "URL": "https://www.cktch.cz/",
        },
        "title": {
            "cs": "Centrum kardiovaskulární a transplantační chirurgie Brno",
            "en": "Centre of Cardiovascular and Transplantation Surgery",
        },
    },
    {
        "id": "centrum-vyzkumu-rez",
        "props": {"ICO": "26722445", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03k9fzs17",
            "URL": "https://www.cvrez.cz/",
        },
        "title": {"cs": "Centrum výzkumu Řež", "en": "Research Centre Řež"},
    },
    {
        "id": "ceska-geologicka-sluzba",
        "props": {"ICO": "00025798", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02xz6bf62",
            "URL": "https://cgs.gov.cz/",
        },
        "title": {"cs": "Česká geologická služba", "en": "Czech Geological Survey"},
    },
    {
        "id": "chmu",
        "props": {"ICO": "00020699", "acronym": "CHMU", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00xbsaf62",
            "URL": "https://www.chmi.cz/",
        },
        "title": {
            "cs": "Český hydrometeorologický ústav",
            "en": "Czech Hydrometeorological Institute",
        },
    },
    {
        "id": "eruni",
        "props": {"ICO": "25840886", "acronym": "ERUNI", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.vs-prigo.cz/"},
        "title": {
            "cs": "Evropská výzkumná univerzita",
            "en": "European Research University",
        },
    },
    {
        "id": "fakultni-nemocnice-bulovka",
        "props": {"ICO": "00064211", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/009e9xr64",
            "URL": "https://bulovka.cz/",
        },
        "title": {
            "cs": "Fakultní nemocnice Bulovka",
            "en": "Bulovka University Hospital",
        },
    },
    {
        "id": "fakultni-nemocnice-hradec-kralove",
        "props": {"ICO": "00179906", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04wckhb82",
            "URL": "https://www.fnhk.cz/",
        },
        "title": {
            "cs": "Fakultní nemocnice Hradec Králové",
            "en": "University Hospital Hradec Králové",
        },
    },
    {
        "id": "fakultni-nemocnice-kralovske-vinohrady",
        "props": {"ICO": "00064173", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04sg4ka71",
            "URL": "https://www.fnkv.cz/",
        },
        "title": {
            "cs": "Fakultní nemocnice Královské Vinohrady",
            "en": "University Hospital Kralovske Vinohrady",
        },
    },
    {
        "id": "fakultni-nemocnice-ostrava",
        "props": {"ICO": "00843989", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00a6yph09",
            "URL": "https://www.fno.cz/",
        },
        "title": {
            "cs": "Fakultní nemocnice Ostrava",
            "en": "University Hospital in Ostrava",
        },
    },
    {
        "id": "fakultni-nemocnice-plzen",
        "props": {"ICO": "00669806", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02c1tfz23",
            "URL": "https://www.fnplzen.cz/",
        },
        "title": {
            "cs": "Fakultní nemocnice Plzeň",
            "en": "University Hospital in Pilsen",
        },
    },
    {
        "id": "fakultni-nemocnice-u-sv.anny-v-brne",
        "props": {"ICO": "00159816", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/049bjee35",
            "URL": "https://www.fnusa.cz/",
        },
        "title": {
            "cs": "Fakultní nemocnice u sv. Anny v Brně",
            "en": "St. Anne's University Hospital Brno",
        },
    },
    {
        "id": "fakultni-nemocnice-v-motole",
        "props": {"ICO": "00064203", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0125yxn03",
            "URL": "https://www.fnmotol.cz/",
        },
        "title": {
            "cs": "Fakultní nemocnice v Motole",
            "en": "Motol University Hospital",
        },
    },
    {
        "id": "fakultni-thomayerova-nemocnice",
        "props": {"ICO": "00064190", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04hyq8434",
            "URL": "https://www.ftn.cz/",
        },
        "title": {
            "cs": "Fakultní Thomayerova nemocnice",
            "en": "Thomayer University Hospital",
        },
    },
    {
        "id": "gacr",
        "props": {"ICO": "48549037", "acronym": "GAČR", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/01pv73b02", "URL": "https://gacr.cz/"},
        "title": {
            "cs": "Grantová agentura České republiky",
            "en": "Czech Science Foundation",
        },
    },
    {
        "id": "ikem",
        "props": {"ICO": "00023001", "acronym": "IKEM", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/036zr1b90",
            "URL": "https://www.ikem.cz/cs/",
        },
        "title": {
            "cs": "Institut klinické a experimentální medicíny",
            "en": "Institute for Clinical and Experimental Medicine",
        },
    },
    {
        "id": "institut-postgradualniho-vzdelavani-ve-zdravotnictvi",
        "props": {"ICO": "00023841", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00rzeqe23",
            "URL": "https://www.ipvz.cz",
        },
        "title": {
            "cs": "Institut postgraduálního vzdělávání ve zdravotnictví",
            "en": "Institute for Postgraduate Medical Education",
        },
    },
    {
        "id": "jihoceska-vedecka-knihovna-v-ceskych-budejovicich",
        "props": {"ICO": "00073504", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03mmhfz41",
            "URL": "https://www.cbvk.cz/",
        },
        "title": {
            "cs": "Jihočeská vědecká knihovna v Českých Budějovicích",
            "en": "Research Library of South Bohemia in České Budějovice",
        },
    },
    {
        "id": "knihovna-města-hradce-kralove",
        "props": {"ICO": "00125491", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.knihovnahk.cz/"},
        "title": {
            "cs": "Knihovna města Hradce Králové",
            "en": "Hradec Králové City Library",
        },
    },
    {
        "id": "knihovna-usteckeho-kraje",
        "props": {"ICO": "00083186", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.knihovnauk.cz/"},
        "title": {"cs": "Knihovna Ústeckého kraje", "en": "Ústí Regional Library"},
    },
    {
        "id": "krajska-knihovna-frantiska-bartose-ve-zline",
        "props": {"ICO": "70947422", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.kfbz.cz/"},
        "title": {
            "cs": "Krajská knihovna Františka Bartoše ve Zlíně",
            "en": "František Bartoš Regional Library in Zlín",
        },
    },
    {
        "id": "krajska-knihovna-v-pardubicich",
        "props": {"ICO": "00085219", "nameType": "organizational"},
        "relatedURI": {"URL": "https://kkpce.cz/cs/"},
        "title": {
            "cs": "Krajská knihovna v Pardubicích",
            "en": "Pardubice Regional Library",
        },
    },
    {
        "id": "krajska-knihovna-vysociny",
        "props": {"ICO": "70950164", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.kkvysociny.cz/"},
        "title": {"cs": "Krajská knihovna Vysočiny", "en": "Vysočina Regional Library"},
    },
    {
        "id": "krajska-vedecka-knihovna-v-liberci",
        "props": {"ICO": "00083194", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.kvkli.cz/"},
        "title": {
            "cs": "Krajská vědecká knihovna v Liberci",
            "en": "Regional Research Library in Liberec",
        },
    },
    {
        "id": "krajska-zdravotni",
        "props": {"ICO": "25488627", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03hdcss70",
            "URL": "https://www.kzcr.eu/",
        },
        "title": {"cs": "Krajská zdravotní", "en": "Regional Health Corporation"},
    },
    {
        "id": "masarykuv-onkologicky-ustav",
        "props": {"ICO": "00209805", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0270ceh40",
            "URL": "https://www.mou.cz/",
        },
        "title": {
            "cs": "Masarykův onkologický ústav",
            "en": "Masaryk Memorial Cancer Institute",
        },
    },
    {
        "id": "membrain",
        "props": {"ICO": "28676092", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05fmr5p93",
            "URL": "https://www.membrain.cz/",
        },
        "title": {"cs": "MemBrain", "en": "MemBrain"},
    },
    {
        "id": "mestska-knihovna-v-praze",
        "props": {"ICO": "00064467", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02kqf1812",
            "URL": "https://www.mlp.cz/cz/",
        },
        "title": {
            "cs": "Městská knihovna v Praze",
            "en": "Municipal Library of Prague",
        },
    },
    {
        "id": "ministerstvo-financ-cr",
        "props": {"ICO": "00006947", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00mjd8b34",
            "URL": "https://www.mfcr.cz/",
        },
        "title": {
            "cs": "Ministerstvo financí ČR",
            "en": "Ministry of Finance of the Czech Republic",
        },
    },
    {
        "id": "msmt",
        "props": {"ICO": "00022985", "acronym": "MŠMT", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/037n8p820",
            "URL": "https://www.msmt.cz/",
        },
        "title": {
            "cs": "Ministerstvo školství, mládeže a tělovýchovy",
            "en": "Ministry of Education, Youth and Sports",
        },
    },
    {
        "id": "moravskoslezska-vedecka-knihovna-v-ostrave",
        "props": {"ICO": "00100579", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0404e3g62",
            "URL": "https://www.msvk.cz/",
        },
        "title": {
            "cs": "Moravskoslezská vědecká knihovna v Ostravě",
            "en": "Moravian-Silesian Research Library in Ostrava",
        },
    },
    {
        "id": "narodni-galerie-v-praze",
        "props": {"ICO": "00023281", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00qd5p471",
            "URL": "https://www.ngprague.cz/",
        },
        "title": {"cs": "Národní galerie v Praze", "en": "National Gallery Prague"},
    },
    {
        "id": "nemocnice-na-homolce",
        "props": {"ICO": "00023884", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00w93dg44",
            "URL": "https://www.homolka.cz/",
        },
        "title": {"cs": "Nemocnice Na Homolce", "en": "Na Homolce Hospital"},
    },
    {
        "id": "prague-film-school",
        "props": {"ICO": "26698099", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02gfwnc58",
            "URL": "https://www.praguefilmschool.cz/",
        },
        "title": {"cs": "Prague Film School", "en": "Prague Film School"},
    },
    {
        "id": "psychiatricka-nemocnice-bohnice-lekarska-knihovna",
        "props": {"ICO": "00064220", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02yrkqr67",
            "URL": "https://bohnice.cz/aktivity/knihovna/",
        },
        "title": {
            "cs": "Psychiatrická nemocnice Bohnice - Lékařská knihovna",
            "en": "Psychiatric Hospital Bohnice - Medical Library",
        },
    },
    {
        "id": "sukl",
        "props": {"ICO": "00023817", "acronym": "SÚKL", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04myyf417",
            "URL": "https://www.sukl.cz/",
        },
        "title": {
            "cs": "Státní ústav pro kontrolu léčiv",
            "en": "State Institute for Drug Control",
        },
    },
    {
        "id": "szu",
        "props": {"ICO": "75010330", "acronym": "SZÚ", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/04ftj7e51", "URL": "https://szu.cz/"},
        "title": {
            "cs": "Státní zdravotní ústav",
            "en": "National Institute of Public Health",
        },
    },
    {
        "id": "stredoceska-vedecka-knihovna-v-kladne",
        "props": {"ICO": "00069892", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/02va58e96", "URL": "https://svkkl.cz/"},
        "title": {
            "cs": "Středočeská vědecká knihovna v Kladně",
            "en": "Central Bohemian Research Library in Kladno",
        },
    },
    {
        "id": "studijni-a-vedecka-knihovna-plzenskeho-kraje",
        "props": {"ICO": "00078077", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/017afg044", "URL": "https://svkpk.cz/"},
        "title": {
            "cs": "Studijní a vědecká knihovna Plzeňského kraje",
            "en": "Education and Research Library of Pilsener Region",
        },
    },
    {
        "id": "studijni-a-vedecka-knihovna-v-hradci-kralove",
        "props": {"ICO": "00412821", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03cd72537",
            "URL": "https://www.svkhk.cz/",
        },
        "title": {
            "cs": "Studijní a vědecká knihovna v Hradci Králové",
            "en": "Research Library in Hradec Králové",
        },
    },
    {
        "id": "tmb",
        "props": {"ICO": "00101435", "acronym": "TMB", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00rb9a558",
            "URL": "https://www.tmbrno.cz/",
        },
        "title": {"cs": "Technické muzeum v Brně", "en": "Technical Museum in Brno"},
    },
    {
        "id": "eli-eric",
        "props": {
            "ICO": "10974938",
            "acronym": "ELI ERIC",
            "nameType": "organizational",
        },
        "relatedURI": {
            "ROR": "https://ror.org/00yzpcc69",
            "URL": "https://eli-laser.eu",
        },
        "title": {
            "cs": "The Extreme Light Infrastructure ERIC",
            "en": "The Extreme Light Infrastructure ERIC (only facility Dolní Břežany, CZ)",
        },
    },
    {
        "id": "urad-vlady-cr",
        "props": {"ICO": "00006599", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/027acbb13",
            "URL": "https://vlada.gov.cz/",
        },
        "title": {
            "cs": "Úřad vlády České republiky",
            "en": "Office of the Government of the Czech Republic",
        },
    },
    {
        "id": "ukht",
        "props": {"ICO": "00023736", "acronym": "ÚHKT", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.uhkt.cz"},
        "title": {
            "cs": "Ústav hematologie a krevní transfuze",
            "en": "Institute of Hematology and Blood Transfusion",
        },
    },
    {
        "id": "vedecka-knihovna-v-olomouci",
        "props": {"ICO": "00100625", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02jh2mm49",
            "URL": "https://www.vkol.cz/",
        },
        "title": {
            "cs": "Vědecká knihovna v Olomouci",
            "en": "Olomouc Research Library",
        },
    },
    {
        "id": "vojenska-nemocnice-brno",
        "props": {"ICO": "60555530", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.vnbrno.cz/"},
        "title": {"cs": "Vojenská nemocnice Brno", "en": "Military Hospital Brno"},
    },
    {
        "id": "vfn",
        "props": {"ICO": "00064165", "acronym": "VFN", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04yg23125",
            "URL": "https://www.vfn.cz/",
        },
        "title": {
            "cs": "Všeobecná fakultní nemocnice v Praze",
            "en": "General University Hospital in Prague",
        },
    },
    {
        "id": "vyzkumny-a-slechtitelsky-ustav-ovocnarsky-holovousy",
        "props": {"ICO": "25271121", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/045c1s446",
            "URL": "https://www.vsuo.cz/cs/",
        },
        "title": {
            "cs": "Výzkumný a šlechtitelský ústav ovocnářský Holovousy",
            "en": "Research and Breeding Institute of Pomology Holovousy",
        },
    },
    {
        "id": "vyzkumny-ustav-bramborarsky-havlickuv-brod",
        "props": {"ICO": "60109807", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/00vcrhv91",
            "URL": "https://www.vubhb.cz/cs",
        },
        "title": {
            "cs": "Výzkumný ústav bramborářský Havlíčkův Brod",
            "en": "Potato Research Institute Havlíčkův Brod",
        },
    },
    {
        "id": "vumop",
        "props": {"ICO": "00027049", "acronym": "VÚMOP", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/045rrq664",
            "URL": "https://www.vumop.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav meliorací a ochrany půdy",
            "en": "Research Institute for Soil and Water Conservation",
        },
    },
    {
        "id": "vyzkumny-ustav-pivovarsky-a-sladarsky",
        "props": {"ICO": "60193697", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/04jr76q91",
            "URL": "https://beerresearch.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav pivovarský a sladařský",
            "en": "Research Institute od Brewing and Malting",
        },
    },
    {
        "id": "vuts-technicka-knihovna",
        "props": {"ICO": "46709002", "acronym": "VÚTS", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02c875652",
            "URL": "https://www.vuts.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav textilních strojů - technická knihovna",
            "en": "VUTS, JSC - Technical Library",
        },
    },
    {
        "id": "vyzkumny-ustav-veterinarniho-lekarstvi",
        "props": {"ICO": "00027162", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02zyjt610",
            "URL": "https://www.vri.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav veterinárního lékařství",
            "en": "Veterinary Research Institute",
        },
    },
    {
        "id": "vuzv",
        "props": {"ICO": "00027014", "acronym": "VÚŽV", "nameType": "organizational"},
        "relatedURI": {"ROR": "https://ror.org/00yb99p92", "URL": "https://vuzv.cz/"},
        "title": {
            "cs": "Výzkumný ústav živočišné výroby",
            "en": "Institute of Animal Science",
        },
    },
    {
        "id": "zemedelsky-vyzkum",
        "props": {"ICO": "26296080", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.vupt.cz/"},
        "title": {"cs": "Zemědělský výzkum", "en": "Agricultural Research"},
    },
    {
        "id": "vyzkumny-ustav-picninarsky",
        "props": {"ICO": "48532452", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/02tjqwz24",
            "URL": "https://www.vupt.cz/",
        },
        "title": {
            "cs": "Výzkumný ústav pícninářský",
            "en": "Research Institute for Fodder Crops",
        },
    },
    {
        "id": "prague-city-university",
        "props": {"ICO": "04264193", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/01x9n3j10",
            "URL": "https://www.praguecityuniversity.cz",
        },
        "title": {"en": "Prague City University"},
    },
    {
        "id": "panevropska-univerzita",
        "props": {"ICO": "04130081", "nameType": "organizational"},
        "relatedURI": {"URL": "https://www.peuni.cz"},
        "title": {"cs": "Panevropská univerzita", "en": "Pan-European University"},
    },
    {
        "id": "indira-gandhi-centre-for-atomic-research",
        "props": {"acronym": "IGCAR", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/05tkzma19",
            "URL": "https://www.igcar.gov.in/hbni.html",
        },
        "title": {"en": "Indira Gandhi Centre for Atomic Research"},
    },
    {
        "id": "institute-of-chemical-engineering-sciences",
        "nonpreferredLabels": [
            {"cs": "FORTH Institute of Chemical Engineering Sciences"}
        ],
        "props": {"acronym": "ICE-HT", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/03e5bsk66",
            "URL": "https://www.iceht.forth.gr",
        },
        "title": {"en": "Institute of Chemical Engineering Sciences"},
    },
    {
        "id": "tescan",
        "nonpreferredLabels": [{"cs": "TESCAN"}],
        "props": {"ICO": "17774713", "nameType": "organizational"},
        "relatedURI": {
            "ROR": "https://ror.org/0556an218",
            "URL": "https://www.tescan.cz",
        },
        "title": {"cs": "TESCAN GROUP"},
    },
    {
        "id": "atelier-krejcirikovi",
        "props": {"ICO": "05291895"},
        "title": {"cs": "Ateliér Krejčiříkovi, s.r.o."},
    },
    {
        "id": "hnuti-duha",
        "nonpreferredLabels": [{"cs": "Hnutí DUHA"}],
        "props": {"ICO": "15547779"},
        "title": {"cs": "Hnutí DUHA - Friends of the Earth Czech Republic"},
    },
    {
        "id": "kroupalide",
        "nonpreferredLabels": [{"cs": "KROUPAHELÁN advokátní kancelář, s.r.o."}],
        "props": {"ICO": "29310571"},
        "title": {"cs": "KROUPALIDÉ advokátní kancelář s.r.o."},
    },
    {
        "id": "sociofactor",
        "nonpreferredLabels": [{"cs": "SocioFactor"}],
        "props": {"ICO": "28586336"},
        "relatedURI": {"ROR": "https://ror.org/01g3ety71"},
        "title": {"cs": "SocioFactor s.r.o."},
    },
    {
        "id": "suip",
        "props": {"ICO": "75046962", "acronym": "SÚIP"},
        "title": {
            "cs": "Státní úřad inspekce práce",
            "en": "State Labour Inspection Office",
        },
    },
    {
        "id": "ujv-rez",
        "nonpreferredLabels": [
            {"cs": "Ústav Jaderného Výzkumu Řež"},
            {"en": "ÚJV Řež, a.\xa0s."},
            {"cs": "UJV Řež"},
        ],
        "props": {"ICO": "46356088", "acronym": "NRI"},
        "relatedURI": {"ROR": "https://ror.org/05gwtvp11"},
        "title": {
            "cs": "Ústav Jaderného Výzkumu Řež, a. s.",
            "en": "Nuclear Research Institute Rez",
        },
    },
    {
        "id": "vsmie",
        "props": {"acronym": "VSMIE"},
        "relatedURI": {"ROR": "https://ror.org/015t1sz24"},
        "title": {
            "cs": "Vysoká škola manažerské informatiky, ekonomiky a práva",
            "en": "College of Information Management Business Administration and Law",
        },
    },
    {
        "id": "edri",
        "nonpreferredLabels": [{"cs": "European Digital Rights"}],
        "props": {"acronym": "EDRi"},
        "title": {"en": "European Digital Rights"},
    },
    {
        "id": "central-european-policy-institute",
        "props": {"acronym": "CEPI"},
        "title": {"en": "Central European Policy Institute"},
    },
    {
        "id": "jihomoravske-dobrovolnicke-centrum",
        "nonpreferredLabels": [
            {"cs": "Plán B, z. s."},
            {"cs": "Plán B, o.s."},
            {"cs": "O.S. Plán B"},
            {"cs": "Občanské sdružení Plán B"},
            {"en": "Dobrovolnické centrum 67"},
        ],
        "props": {"ICO": "26517230"},
        "title": {"cs": "Jihomoravské dobrovolnické centrum z.s."},
    },
    {
        "id": "dcul",
        "props": {"ICO": "70225842", "acronym": "DCUL"},
        "title": {"cs": "Dobrovolnické centrum, z. s."},
    },
    {
        "id": "nidm",
        "props": {"acronym": "NIDM"},
        "tags": ["deprecated"],
        "title": {"cs": "Národní institut dětí a mládeže MŠMT"},
    },
    {
        "id": "wipo",
        "props": {"acronym": "WIPO"},
        "relatedURI": {"ROR": "https://ror.org/04anve402"},
        "title": {
            "cs": "Světová organizace duševního vlastnictví",
            "en": "World Intellectual Property Organization",
        },
    },
    {
        "id": "euipo",
        "nonpreferredLabels": [
            {"cs": "Úřad pro harmonizaci na vnitřním trhu"},
            {"cs": "Úřad pro harmonizaci ve vnitřním trhu"},
            {"en": "OHIM"},
            {"en": "Office for Harmonization in the Internal Market"},
        ],
        "props": {"acronym": "EUIPO"},
        "relatedURI": {"URL": "https://www.euipo.europa.eu/"},
        "title": {
            "cs": "Úřad Evropské unie pro duševní vlastnictví",
            "en": "European Union Intellectual Property Office",
        },
    },
    {
        "id": "migration-policy-task-force",
        "title": {"en": "Migration Policy Task Force"},
    },
    {
        "id": "infodatasys",
        "props": {"ICO": "43838243"},
        "title": {"cs": "Ing. Karel MATĚJKA, CSc.-IDS"},
    },
    {
        "id": "norwegian-forest-and-landscape-institute",
        "title": {"en": "Norwegian Forest and Landscape Institute"},
    },
    {
        "id": "isga",
        "props": {"acronym": "ISGA"},
        "title": {"en": "International School Grounds Alliance"},
    },
    {
        "id": "staatsbetrieb-sachsenforst",
        "props": {"acronym": "SbS"},
        "title": {"cs": "Staatsbetrieb Sachsenforst"},
    },
    {
        "id": "cs-ustav-pro-vyzkum-verejneho-mineni",
        "nonpreferredLabels": [{"cs": "Ústav pro výzkum veřejného mínění"}],
        "tags": ["deprecated"],
        "title": {"cs": "Československý ústav pro výzkum veřejného mínění"},
    },
    {
        "id": "uni-bergen",
        "props": {"acronym": "UiB"},
        "relatedURI": {
            "ROR": "https://ror.org/03zga2b32",
            "URL": "https://www.uib.no/en",
        },
        "nonpreferredLabels": [{"no": "Universitetet i Bergen"}],
        "title": {"en": "University of Bergen"},
    },
    {
        "id": "uni-bayreuth",
        "relatedURI": {
            "ROR": "https://ror.org/0234wmv40",
            "URL": "https://www.uni-bayreuth.de/en",
        },
        "nonpreferredLabels": [{"de": "Universität Bayreuth"}],
        "title": {"en": "University of Bayreuth"},
    },
    {
        "id": "mpsv",
        "props": {"acronym": "MPSV", "ICO": "00551023"},
        "relatedURI": {
            "ROR": "https://ror.org/01bvj3e58",
            "URL": "http://www.mpsv.cz/",
        },
        "nonpreferredLabels": [
            {"en": "MoLSA"},
            {"cs": "Ministerstvo práce a sociálních věcí"},
            {"cs": "Ministerstvo práce a sociálních věcí ČR"},
        ],
        "title": {
            "cs": "Ministerstvo práce a sociálních věcí České republiky",
            "en": "Ministry of Labour and Social Affairs",
        },
    },
    {
        "id": "mvcr",
        "props": {"acronym": "MVCR", "ICO": "00007064"},
        "relatedURI": {
            "ROR": "https://ror.org/05w1nn565",
            "URL": "http://www.mvcr.cz/",
        },
        "nonpreferredLabels": [
            {"cs": "Ministerstvo vnitra"},
            {"cs": "Ministerstvo vnitra ČR"},
        ],
        "title": {
            "cs": "Ministerstvo vnitra České republiky",
            "en": "Ministry of the Interior",
        },
    },
    {
        "id": "mkcr",
        "props": {"acronym": "MKČR", "ICO": "00023671"},
        "relatedURI": {
            "ROR": "https://ror.org/00fxxw604",
            "URL": "http://www.mkcr.cz/",
        },
        "nonpreferredLabels": [
            {"cs": "Ministerstvo Kultury"},
            {"cs": "Ministerstvo Kultury ČR"},
        ],
        "title": {
            "cs": "Ministerstvo Kultury České Republiky",
            "en": "Ministry of Culture",
        },
    },
    {
        "id": "goethe-institut",
        "props": {"acronym": "GI"},
        "relatedURI": {
            "ROR": "https://ror.org/02szraf30",
            "URL": "https://www.goethe.de/",
        },
        "title": {"de": "Goethe Institut", "en": "Goethe Institute"},
    },
    {
        "id": "iucn",
        "props": {"acronym": "IUCN"},
        "relatedURI": {
            "ROR": "https://ror.org/01szdrn56",
            "URL": "http://www.iucn.org/",
        },
        "nonpreferredLabels": [
            {"en": "IUCN/SSC"},
            {
                "en": "International Union for Conservation of Nature and Natural Resources"
            },
        ],
        "title": {"en": "International Union for Conservation of Nature"},
    },
    {
        "id": "greynet",
        "relatedURI": {
            "ROR": "https://ror.org/01pxfxj80",
            "URL": "https://www.greynet.org",
        },
        "nonpreferredLabels": [{"en": "Grey Literature Network Service"}],
        "title": {"en": "GreyNet International"},
    },
    {
        "id": "stu",
        "props": {"acronym": "STU"},
        "relatedURI": {
            "ROR": "https://ror.org/0561ghm58",
            "URL": "https://www.stuba.sk/",
        },
        "title": {
            "sk": "Slovenská technická univerzita v Bratislave",
            "en": "Slovak University of Technology in Bratislava",
        },
    },
    {
        "id": "fu-berlin",
        "props": {"acronym": "FU"},
        "relatedURI": {
            "ROR": "https://ror.org/046ak2485",
            "URL": "https://www.fu-berlin.de",
        },
        "nonpreferredLabels": [{"en": "FU Berlin"}],
        "title": {"en": "Free University of Berlin", "de": "Freie Universität Berlin"},
    },
    {
        "id": "qub",
        "props": {"acronym": "QUB"},
        "relatedURI": {
            "ROR": "https://ror.org/00hswnk62",
            "URL": "https://www.qub.ac.uk",
        },
        "title": {"cy": "Prifysgol y Frenhines", "en": "Queen's University Belfast"},
    },
    {
        "id": "uni-manchester",
        "relatedURI": {
            "ROR": "https://ror.org/027m9bs27",
            "URL": "https://www.manchester.ac.uk",
        },
        "title": {"en": "University of Manchester"},
    },
    {
        "id": "elte",
        "props": {"acronym": "ELTE"},
        "relatedURI": {
            "ROR": "https://ror.org/01jsq2704",
            "URL": "https://www.elte.hu",
        },
        "title": {
            "hu": "Eötvös Loránd Tudományegyetem",
            "en": "Eötvös Loránd University",
        },
    },
    {
        "id": "stfc",
        "props": {"acronym": "STFC"},
        "relatedURI": {
            "ROR": "https://ror.org/057g20z61",
            "URL": "https://www.ukri.org/councils/stfc/",
        },
        "title": {"en": "Science and Technology Facilities Council"},
    },
    {
        "id": "hartree-centre",
        "nonpreferredLabels": [
            {"en": "Science and Technology Facilities Council’s (STFC) Hartree Centre"},
            {"en": "STFC Hartree Centre"},
        ],
        "relatedURI": {"URL": "https://www.hartree.stfc.ac.uk/"},
        "title": {"en": "Hartree Centre"},
    },
    {
        "id": "uni-toronto",
        "relatedURI": {
            "ROR": "https://ror.org/03dbr7087",
            "URL": "https://www.utoronto.ca/",
        },
        "nonpreferredLabels": [{"fr": "Université de Toronto"}],
        "title": {"en": "University of Toronto"},
    },
    {
        "id": "wigner",
        "props": {"acronym": "MTA Wigner RC"},
        "relatedURI": {
            "ROR": "https://ror.org/035dsb084",
            "URL": "https://wigner.hu/en",
        },
        "nonpreferredLabels": [{"en": "Wigner RCP"}],
        "title": {
            "hu": "Wigner Fizikai Kutatóközpont",
            "en": "Wigner Research Centre for Physics",
        },
    },
    {
        "id": "tum",
        "props": {"acronym": "TUM"},
        "relatedURI": {"ROR": "https://ror.org/02kkvpp62", "URL": "https://www.tum.de"},
        "title": {
            "de": "Technische Universität München",
            "en": "Technical University of Munich",
        },
    },
    {
        "id": "metu",
        "props": {"acronym": "ODTÜ"},
        "relatedURI": {
            "ROR": "https://ror.org/014weej12",
            "URL": "https://www.metu.edu.tr",
        },
        "title": {
            "tr": "Orta Doğu Teknik Üniversitesi",
            "en": "Middle East Technical University",
        },
    },
    {
        "id": "vu",
        "props": {"acronym": "VU"},
        "relatedURI": {"ROR": "https://ror.org/008xxew50", "URL": "https://vu.nl/"},
        "nonpreferredLabels": [{"en": "VU Amsterdam"}],
        "title": {"en": "Vrije Universiteit Amsterdam"},
    },
    {
        "id": "uniba",
        "relatedURI": {"ROR": "https://ror.org/0587ef340", "URL": "https://uniba.sk/"},
        "nonpreferredLabels": [
            {"hu": "Comenius Egyetem"},
            {"de": "Comenius-Universität Bratislava"},
            {"es": "Universidad Comenius de Bratislava"},
            {"la": "Universitas Comeniana Bratislavensis"},
            {"fr": "Université Commenius de Bratislava"},
        ],
        "title": {
            "sk": "Univerzita Komenského v Bratislave",
            "en": "Comenius University Bratislava",
        },
    },
    {
        "id": "nscc",
        "props": {"acronym": "NSCC"},
        "relatedURI": {"URL": "https://nscc.sk/"},
        "title": {
            "sk": "Národné superpočítačové centrum",
            "en": "Slovak National Supercomputing Centre",
        },
    },
    {
        "id": "vssav",
        "props": {"acronym": "VS SAV"},
        "relatedURI": {"URL": "https://vs.sav.sk/"},
        "title": {
            "sk": "Výpočtové stredisko Slovenskej akadémie vied",
            "en": "Computing Centre of the Slovak Academy od Sciences",
        },
    },
    {
        "id": "am-uni",
        "props": {"acronym": "AMU"},
        "relatedURI": {
            "ROR": "https://ror.org/035xkbk20",
            "URL": "http://www.univ-amu.fr/",
        },
        "nonpreferredLabels": [
            {"en": "Paul Cézanne University"},
            {"en": "University of Provence"},
            {"en": "University of the Mediterranean"},
            {"fr": "Université d'Aix-Marseille"},
        ],
        "title": {"fr": "Aix-Marseille Université", "en": "Aix-Marseille University"},
    },
    {
        "id": "iuf",
        "props": {"acronym": "IUF"},
        "relatedURI": {
            "ROR": "https://ror.org/055khg266",
            "URL": "http://iuf.amue.fr/",
        },
        "title": {"fr": "Institut Universitaire de France"},
    },
    {
        "id": "xmu",
        "props": {"acronym": "XMU"},
        "relatedURI": {
            "ROR": "https://ror.org/00mcjh785",
            "URL": "https://www.xmu.edu.cn",
        },
        "title": {"zh": "Xiàmén Dàxué", "en": "Xiamen University"},
    },
    {
        "id": "umk",
        "props": {"acronym": "UMK"},
        "relatedURI": {"ROR": "https://ror.org/0102mm775", "URL": "https://www.umk.pl"},
        "title": {
            "pl": "Uniwersytet Mikołaja Kopernika w Toruniu",
            "en": "Nicolaus Copernicus University",
        },
    },
    {
        "id": "likat",
        "props": {"acronym": "LIKAT"},
        "relatedURI": {
            "ROR": "https://ror.org/029hg0311",
            "URL": "https://www.catalysis.de",
        },
        "nonpreferredLabels": [{"de": "LIKAT Rostock"}],
        "title": {
            "de": "Leibniz-Institut für Katalyse e.V.",
            "en": "Leibniz Institute for Catalysis",
        },
    },
    {
        "id": "uni-graz",
        "relatedURI": {
            "ROR": "https://ror.org/01faaaf77",
            "URL": "https://www.uni-graz.at/en/",
        },
        "nonpreferredLabels": [
            {"la": "Carolo Franciscea Graecensis"},
            {"de": "Karl-Franzens-Universität Graz"},
            {"hr": "Sveučilište u Grazu"},
            {"sl": "Univerza v Gradcu"},
        ],
        "title": {"en": "University of Graz"},
    },
    {
        "id": "dtu",
        "props": {"acronym": "DTU"},
        "relatedURI": {
            "ROR": "https://ror.org/04qtj9h94",
            "URL": "https://dtu.dk",
        },
        "nonpreferredLabels": [
            {"de": "Dänemarks Technische Universität"},
        ],
        "title": {
            "da": "Danmarks Tekniske Universitet",
            "en": "Technical University of Denmark",
        },
    },
    {
        "id": "syft",
        "relatedURI": {"URL": "https://syft.com/"},
        "title": {
            "en": "Syft Technologies",
        },
    },
    {
        "id": "vinci",
        "relatedURI": {"URL": "https://www.davinci-ls.com/en-us/home"},
        "title": {
            "en": "Da Vinci Laboratory Solutions UK & Ireland",
        },
    },
]
