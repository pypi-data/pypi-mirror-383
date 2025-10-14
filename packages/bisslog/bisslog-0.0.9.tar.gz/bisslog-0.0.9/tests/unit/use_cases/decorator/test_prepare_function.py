"""Unit tests for prepare_function in use_case_decorator module."""

import bisslog.use_cases.use_case_decorator.prepare_function as pf_mod

prepare_function = pf_mod.prepare_function


def test_keyname_defaults_to_function_name(monkeypatch):
    monkeypatch.setattr(pf_mod, "is_free_function", lambda fn: False, raising=True)

    def sample():
        pass

    key, accepts_tid = prepare_function(sample, keyname=None, do_trace=True)
    assert key == "sample"
    assert accepts_tid is False


def test_keyname_uses_custom_when_provided(monkeypatch):
    monkeypatch.setattr(pf_mod, "is_free_function", lambda fn: False, raising=True)

    def f():
        pass

    key, accepts_tid = prepare_function(f, keyname="custom-key", do_trace=True)
    assert key == "custom-key"
    assert accepts_tid is False


def test_accepts_tid_true_when_do_trace_and_param_present(monkeypatch):
    monkeypatch.setattr(pf_mod, "is_free_function", lambda fn: False, raising=True)

    def with_tid(transaction_id=None):
        pass

    key, accepts_tid = prepare_function(with_tid, keyname=None, do_trace=True)
    assert key == "with_tid"
    assert accepts_tid is True


def test_accepts_tid_true_when_do_trace_and_var_keyword(monkeypatch):
    monkeypatch.setattr(pf_mod, "is_free_function", lambda fn: False, raising=True)

    def with_kwargs(**kwargs):
        pass

    key, accepts_tid = prepare_function(with_kwargs, keyname=None, do_trace=True)
    assert key == "with_kwargs"
    assert accepts_tid is True


def test_accepts_tid_false_when_do_trace_true_but_no_tid_nor_kwargs(monkeypatch):
    monkeypatch.setattr(pf_mod, "is_free_function", lambda fn: False, raising=True)

    def plain(a, b):
        pass

    key, accepts_tid = prepare_function(plain, keyname=None, do_trace=True)
    assert key == "plain"
    assert accepts_tid is False


def test_accepts_tid_false_when_do_trace_false_even_if_tid_present(monkeypatch):
    monkeypatch.setattr(pf_mod, "is_free_function", lambda fn: False, raising=True)

    def with_tid(transaction_id=None):
        pass

    key, accepts_tid = prepare_function(with_tid, keyname=None, do_trace=False)
    assert key == "with_tid"
    assert accepts_tid is False


def test_sets_dunder_is_use_case_when_is_free_function_true(monkeypatch):
    monkeypatch.setattr(pf_mod, "is_free_function", lambda fn: True, raising=True)

    def free_fn():
        pass

    key, accepts_tid = prepare_function(free_fn, keyname=None, do_trace=False)
    assert key == "free_fn"
    assert accepts_tid is False
    assert getattr(free_fn, "__is_use_case__", False) is True


def test_does_not_set_dunder_is_use_case_when_is_free_function_false(monkeypatch):
    monkeypatch.setattr(pf_mod, "is_free_function", lambda fn: False, raising=True)

    def not_free():
        pass

    key, accepts_tid = prepare_function(not_free, keyname=None, do_trace=False)
    assert key == "not_free"
    assert accepts_tid is False
    assert "__is_use_case__" not in vars(not_free)


def test_does_not_crash_if_function_already_has_is_use_case(monkeypatch):
    monkeypatch.setattr(pf_mod, "is_free_function", lambda fn: False, raising=True)

    def already_tagged():
        pass

    already_tagged.__is_use_case__ = "keep"
    key, accepts_tid = prepare_function(already_tagged, keyname=None, do_trace=True)
    assert key == "already_tagged"
    assert accepts_tid is False
    assert already_tagged.__is_use_case__ == "keep"
