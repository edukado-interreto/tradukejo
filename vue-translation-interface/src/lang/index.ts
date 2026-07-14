import ca from "./ca.json"
import cs from "./cs.json"
import en from "./en.json"
import eo from "./eo.json"
import fi from "./fi.json"
import fr from "./fr.json"
import it from "./it.json"
import ms from "./ms.json"
import nl from "./nl.json"
import pl from "./pl.json"
import pt from "./pt.json"
import sk from "./sk.json"

const LANGUAGES = { ca, cs, en, eo, fi, fr, it, ms, nl, pl, pt, sk }

export default { ...LANGUAGES, "en-US": en }
