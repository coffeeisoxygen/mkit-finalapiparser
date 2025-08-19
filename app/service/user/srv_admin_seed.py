"""this class is about default administrator seeding.

case:
    when theres no administrator user its will seed default admin user.
    then it will create a new user with is_superuser = true.
condition to meet:
    - jika tidak ada satupun record user dengan is_superuser = true
    - jika ada record user dengan is_superuser = true, maka tidak perlu melakukan seeding
"""
