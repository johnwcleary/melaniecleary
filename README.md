# melaniecleary.com

A static rebuild of Melanie Cleary's portfolio, which was on Squarespace. No frameworks and no dependencies beyond Python 3.

```
content.json   ← all the words, project order, video IDs and image names
build.py       ← turns content.json into the HTML pages in site/
site/          ← the finished website (this folder is what gets deployed)
  assets/css/style.css
  assets/js/main.js   (photo-gallery lightbox)
  assets/img/         (images and GIFs downloaded from the old site)
```

## Editing

1. Change `content.json` (add a project, reorder the grid, fix copy). Put any new images in `site/assets/img/`.
2. Run `python3 build.py`.
3. Preview with `python3 -m http.server 8742 --directory site` and open http://localhost:8742.

Block types you can use inside a project's `blocks`:

| type      | fields |
|-----------|--------|
| `text`    | `html`: list of paragraphs (can contain `<em>`, `<a>`) |
| `video`   | `id` (Vimeo ID), `h` (private-link hash, if the video is unlisted), `ratio` like `"16/9"`, `"9/16"`, `"4/5"`, `title` |
| `image`   | `src` (file in `site/assets/img`), `alt` |
| `row`     | `items`: blocks shown side by side; optional `cols`, `align: "center"` |
| `gallery` | `items`: `{src, alt}` photos, opened in a lightbox on click |
| `credits` / `awards` | `items`: `[label, value]` pairs |

## Deploying

`site/` is plain HTML, so it works on any static host (Netlify, Vercel, Cloudflare Pages, GitHub Pages). Point the host at the `site` folder; no build step is required on the host as long as you commit the generated pages. Project URLs match the old Squarespace ones (`/invisalign`, `/about`, …), so existing links keep working.

Videos are still hosted on Vimeo. Don't delete them from that Vimeo account.
