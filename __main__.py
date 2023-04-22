import sys
import factorize

rc = 1
try:
    factorize.main(sys.argv)
    rc = 0
except Exception as e:
    print('Error: %s' % e, file=sys.stderr)
sys.exit(rc)
