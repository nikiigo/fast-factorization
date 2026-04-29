import sys
import factorize

try:
    rc = factorize.main(sys.argv)
except Exception as e:
    print('Error: %s' % e, file=sys.stderr)
    rc = 1
sys.exit(rc)
