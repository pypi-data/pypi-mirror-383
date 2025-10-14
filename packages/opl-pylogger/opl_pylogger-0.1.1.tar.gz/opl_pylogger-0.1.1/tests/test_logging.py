import io, sys
from src.opl_logger import init, get_logger

def test_emits_json(monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buf)
    init('test', 'test', '0.0.0', json_stdout=True)
    log = get_logger('t')
    log.info('ok', attrs={'http.request.method': 'GET'})
    txt = buf.getvalue().strip()
    assert txt.startswith('{') and 'severity_text' in txt