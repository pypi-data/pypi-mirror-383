from io import StringIO
import sys


def test_main_prints_message():
    import main
    buf = StringIO()
    old = sys.stdout
    try:
        sys.stdout = buf
        main.main()
    finally:
        sys.stdout = old
    assert "Hello from sibr-agent!" in buf.getvalue()

