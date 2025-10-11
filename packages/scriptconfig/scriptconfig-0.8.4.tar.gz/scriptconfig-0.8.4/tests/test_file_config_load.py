import scriptconfig as scfg
import os
import ubelt as ub


def mark_requires_yaml():
    try:
        import yaml  # NOQA
    except ImportError:
        import pytest
        pytest.skip('requires yaml')


def test_json_dump():
    import json
    dpath = ub.Path.appdir('scriptconfig', 'tests', 'test_file_config').ensuredir()
    class MyConfig(scfg.DataConfig):
        option1 = 'a'
        option2 = 'b'
        option3 = 'c'
    config = MyConfig(option1=2, option2='foobar')
    fpath = dpath / 'test_dump_config.json'
    with open(fpath, 'w') as file:
        config.dump(file, mode='json')
    recon = json.loads(fpath.read_text())
    assert recon == dict(config)


def test_yaml_dump():
    mark_requires_yaml()
    dpath = ub.Path.appdir('scriptconfig', 'tests', 'test_file_config').ensuredir()
    class MyConfig(scfg.DataConfig):
        option1 = 'a'
        option2 = 'b'
        option3 = 'c'
    config = MyConfig(option1=2, option2='foobar')
    fpath = dpath / 'test_dump_config.yaml'
    with open(fpath, 'w') as file:
        config.dump(file, mode='yaml')
    print(fpath.read_text())
    assert fpath.read_text() == 'option1: 2\noption2: foobar\noption3: c\n'


def test_yaml_load():
    mark_requires_yaml()
    dpath = ub.Path.appdir('scriptconfig', 'tests', 'test_file_config').ensuredir()
    class MyConfig(scfg.DataConfig):
        option1 = 'a'
        option2 = 'b'
        option3 = 'c'
    config = MyConfig(option1=3, option2='baz')
    fpath = dpath / 'test_load_config.yaml'
    with open(fpath, 'w') as file:
        config.dump(file, mode='yaml')

    config2 = MyConfig()
    # Test works with string
    config2.load(data=os.fspath(fpath))
    assert dict(config2) == dict(config)

    config2 = MyConfig()
    # Test works with pathlib
    config2.load(data=fpath)
    assert dict(config2) == dict(config)


def test_json_load():
    dpath = ub.Path.appdir('scriptconfig', 'tests', 'test_file_config').ensuredir()
    class MyConfig(scfg.DataConfig):
        option1 = 'a'
        option2 = 'b'
        option3 = 'c'
    config = MyConfig(option1=3, option2='baz')
    fpath = dpath / 'test_load_config.json'
    with open(fpath, 'w') as file:
        config.dump(file, mode='json')

    config2 = MyConfig()
    # Test works with string
    config2.load(data=os.fspath(fpath))
    assert dict(config2) == dict(config)

    config2 = MyConfig()
    # Test works with pathlib
    config2.load(data=fpath)
    assert dict(config2) == dict(config)


def test_config_dumps_load_cli():
    mark_requires_yaml()
    dpath = ub.Path.appdir('scriptconfig', 'tests', 'test_file_config').ensuredir()
    class MyConfig(scfg.DataConfig):
        option1 = 'a'
        option2 = 'b'
        option3 = 'c'
    fpath = dpath / 'test_dump_load_config.json'
    fpath.delete()
    assert not fpath.exists()
    config = MyConfig(option1=3, option2='baz')
    try:
        MyConfig.cli(argv=['--option1=dumped', '--dump', os.fspath(fpath)])
    except SystemExit:
        assert fpath.exists()

    config = MyConfig.cli(argv=['--config', os.fspath(fpath)])
    assert config['option1'] == 'dumped'


def test_config_load_from_json_text():
    """
    Check that the config can load from raw text on the command line
    """
    class MyConfig(scfg.DataConfig):
        option1 = 'a'
        option2 = 'b'
        option3 = 'c'
    config = MyConfig(option1=3, option2='baz')
    config2 = MyConfig.cli(argv=['--config', config.dumps(mode='json')])
    assert dict(config2) == dict(config)


def test_config_load_from_yaml_text():
    """
    Check that the config can load from raw text on the command line
    """
    mark_requires_yaml()
    class MyConfig(scfg.DataConfig):
        option1 = 'a'
        option2 = 'b'
        option3 = 'c'
    config = MyConfig(option1=3, option2='baz')
    config2 = MyConfig.cli(argv=['--config', config.dumps(mode='yaml')])
    assert dict(config2) == dict(config)
