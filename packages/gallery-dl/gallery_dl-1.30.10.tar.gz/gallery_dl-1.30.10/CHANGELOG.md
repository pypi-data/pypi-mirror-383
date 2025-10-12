## 1.30.10 - 2025-10-12
### Extractors
#### Additions
- [bluesky] add `bookmark` extractor ([#8370](https://github.com/mikf/gallery-dl/issues/8370))
- [dandadan] add support ([#8381](https://github.com/mikf/gallery-dl/issues/8381))
#### Fixes
- [bellazon] fix video URL extraction ([#8392](https://github.com/mikf/gallery-dl/issues/8392))
- [bluesky] handle exceptions during file extraction
- [civitai] prevent downloading random posts from deleted users ([#8299](https://github.com/mikf/gallery-dl/issues/8299))
- [girlsreleased] update API endpoints ([#8360](https://github.com/mikf/gallery-dl/issues/8360))
- [instagram] restore `video_dash_manifest` downloads ([#8364](https://github.com/mikf/gallery-dl/issues/8364))
- [kemono] prevent fatal exceptions when retrieving user profile data ([#8382](https://github.com/mikf/gallery-dl/issues/8382))
- [mangadex] fix `RuntimeError` for titles without a `description` ([#8389](https://github.com/mikf/gallery-dl/issues/8389))
- [naver-blog] fix video extraction ([#8385](https://github.com/mikf/gallery-dl/issues/8385))
- [poipiku] fix original file downloads ([#8356](https://github.com/mikf/gallery-dl/issues/8356))
- [weibo] fix retrieving followers-only content ([#6447](https://github.com/mikf/gallery-dl/issues/6447) [#7939](https://github.com/mikf/gallery-dl/issues/7939) [#8063](https://github.com/mikf/gallery-dl/issues/8063) [#8354](https://github.com/mikf/gallery-dl/issues/8354) [#8357](https://github.com/mikf/gallery-dl/issues/8357))
- [weibo] use `page` parameter for `feed` results ([#7523](https://github.com/mikf/gallery-dl/issues/7523) [#8128](https://github.com/mikf/gallery-dl/issues/8128) [#8357](https://github.com/mikf/gallery-dl/issues/8357))
- [wikimedia] fix name & extension of files without an extension ([#8344](https://github.com/mikf/gallery-dl/issues/8344))
- [wikimedia] ignore missing files ([#8388](https://github.com/mikf/gallery-dl/issues/8388))
#### Improvements
- [bellazon] ignore links to other threads ([#8392](https://github.com/mikf/gallery-dl/issues/8392))
- [common] disable delay for `request_location()`
- [fansly] update format selection ([#4401](https://github.com/mikf/gallery-dl/issues/4401))
- [fansly] download user posts from all account walls ([#4401](https://github.com/mikf/gallery-dl/issues/4401))
- [instagram] support `/share/SHORTCODE` URLs ([#8340](https://github.com/mikf/gallery-dl/issues/8340))
- [weibo] ignore ongoing live streams ([#8339](https://github.com/mikf/gallery-dl/issues/8339))
- [zerochan] forward URL parameters to API requests ([#8377](https://github.com/mikf/gallery-dl/issues/8377))
#### Metadata
- [instagram] extract `subscription` metadata ([#8349](https://github.com/mikf/gallery-dl/issues/8349))
- [webtoons] fix `episode` metadata extraction ([#2591](https://github.com/mikf/gallery-dl/issues/2591))
#### Removals
- [twitter] remove login support ([#4202](https://github.com/mikf/gallery-dl/issues/4202) [#6029](https://github.com/mikf/gallery-dl/issues/6029) [#6040](https://github.com/mikf/gallery-dl/issues/6040) [#8362](https://github.com/mikf/gallery-dl/issues/8362))
### Post Processors
- [exec] support `{_temppath}` replacement fields ([#8329](https://github.com/mikf/gallery-dl/issues/8329))
### Miscellaneous
- [formatter] improve error messages ([#8369](https://github.com/mikf/gallery-dl/issues/8369))
- [path] implement conditional `base-directory`
- use `utf-8` encoding when opening files in text mode ([#8376](https://github.com/mikf/gallery-dl/issues/8376))
