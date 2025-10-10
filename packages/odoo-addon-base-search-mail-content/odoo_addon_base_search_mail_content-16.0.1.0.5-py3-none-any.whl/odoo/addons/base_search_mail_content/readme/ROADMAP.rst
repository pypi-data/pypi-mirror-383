This module restricts the message_content search functionality
to internal users only, addressing the issue faced by project collaborators (portal users)
as described in https://github.com/OCA/social/issues/1204. Consequently, portal users no
longer have the ability to search within mail content.

This module's usability is severely limited for languages that don't separate words with spaces (e.g., Chinese, Japanese, Korean, Thai, etc.), 
because `pg_trgm` needs three-character tokens and a similarity score above the default cutoff