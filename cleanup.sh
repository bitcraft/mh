find . -name \.DS_Store -type f -delete
find . -name \*~ -type f -delete
find . -name \*pyc -type f -delete
find . -name \*.swp -type f -delete
find . -type d -print0 | xargs -0 chmod 755
find . -type f -print0 | xargs -0 chmod 644
find . -type f -print0 | xargs -0 touch -ma
