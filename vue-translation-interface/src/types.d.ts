type LanguageCode = string

// Models

type Person = {
  id: number
  username: string
  profile_url: string
}

type Language = {
  id: number
  code: LanguageCode
  name: string
  direction: "ltr" | "rtl"
  google: string
  yandex: string
  deepl: string
  plural_examples_list: string[]
}

type TrString = {
  id: number
  name: string
  path: string
  context: string
  original_text: TrStringText
  translated_text: TrStringText
  state: number
  translated_languages: Record<string, string>
  deleted?: boolean
}

type TrStringText = {
  id: number
  language: Language
  pluralized: boolean
  raw_text: Record<number, string>
  text: Record<number, string>
  last_change: date
  old_versions: number
  comments: TranslationComment[]
  translated_by?: Person
}

type TranslationComment = {
  id: number
  text: string
  create_date: date
  author?: Person
}

type Project = {}

type LanguageVersion = {}

type TranslatorRequest = {}

type TrStringTextHistory = {
  id: number
  pluralized: boolean
  create_date: date
  comparison: Record<string, string>
  translated_by: Person
}

type StringActivity = {}

// Directory tree

type NodeName = string

type DirectoryTree = Record<NodeName, DirectoryTreeNode>

type DirectoryTreeNode = {
  children: TreeNode
  strings: NodeInfo
  strings_in_children: NodeInfo
}

type NodeInfo = {
  count: number
  characters: number
  words: number
}

// Store

type FetchStringsPayload = {
  dir: string
  q: string
  sort: string
  state: string
  chosen_string?: number | null
}

type FetchTreePayload = {
  q: string
  state: string
}

type UpdateStringStatePayload = {
  id: number
  translated: boolean
}

type TranslationData = {
  trstring_id: number
  text: string[]
  name: string
  path: string
  pluralized: boolean
  context: string
  minor: boolean
}

type InsertSymbol = {
  index: number
  stringId: number | string
  text: string
}
