// Notice that:
// * top-level objects group all differing suggestions
// * for every translation there might be multiple original phrases that
//   were translated the same way
// * count within the top-level object is a sum of the counts of the
//   objects on the "projects" list.
[ {"text": "Simpan Sebagai", // proposed translation
   "value": 1, // the lower, the better
   "count": 4, // total number of occurences of phrase "Simpan Sebagai"
   "projects": [
         {"count": 4, // number of occurences of this phrase in GNOME
          "flags": 0, // 0 means OK, 1 means fuzzy
          "name": "GNOME", // name of the project
          "orig_phrase": "Save As", // original phrase in the project
          "path": "G/evolution"}]},
  {"text": "Simpan Sebagai...",
   "value": 1,
   "count": 2,
   "projects": [
         {"count": 1,
          "flags": 0,
          "name": "GNOME",
          "orig_phrase": "Save As…",
          "path": "G/gedit"},
         {"count": 1,
          "flags": 0,
          "name": "GNOME",
          "orig_phrase": "Save As...",
          "path": "G/evolution"}]}
]
