import pytest
from typing import Dict, Any
from cliify import commandParser, command

# Test fixtures and helper classes



@commandParser
class DeviceBase:
    def __init__(self, name: str):
        self.name = name
        
    @command(help="Simple test command")
    def test_command(self, arg1: int, arg2: str = "default"):
        return f"Received {arg1} and {arg2}"

@commandParser
class DeviceSub(DeviceBase):
    def __init__(self, name: str):
        super().__init__(name)
        
    @command(help="Sub command")
    def sub_command(self, arg1: int):
        return f"Sub command received {arg1}"   

@commandParser
class DeviceComplex:
    def __init__(self, name: str):
        self.name = name
        self.data = {}
        
    @command(help="Store data with label")
    def store_data(self, label: str = None, data: bytes = None):
        self.data[label] = data
        return len(data)

@commandParser(subparsers=['devices'])
class InterfaceBase:
    def __init__(self, name: str):
        self.name = name
        self.devices: Dict[str, DeviceBase] = {}

    def get_completions(self):
        return [0,1738]
        
    @command(help="Add two numbers", completions={'a': [1, 2, 3, 4, 5], 'b': lambda self: self.get_completions()})
    def add_numbers(self, a: int, b: int):
        return a + b
    
    @command(help="Subtract two numbers", completions={'a': lambda self: self.get_completions()})
    def sub_numbers(self, a: int, b: int):
        return a - b
    
    def add_device(self, device):
        self.devices[device.name] = device

@commandParser(allow_eval=True, subparsers=['interfaces', 'mainInterface', 'extraInterfaces'])
class SessionBase:
    def __init__(self):

        self.interfaces: Dict[str, InterfaceBase] = {}

        self.mainInterface = InterfaceBase('main')
    
    def add_interface(self, interface):
        self.interfaces[interface.name] = interface

@pytest.fixture
def setup_session():
    session = SessionBase()
    interface = InterfaceBase('test_interface')
    device = DeviceBase('test_device')
    interface.add_device(device)
    session.add_interface(interface)
    return session

def test_simple_command():
    device = DeviceBase('test')
    result = device.parseCommand("test_command arg1: 42")
    assert result == "Received 42 and default"
    
    result = device.parseCommand("test_command arg1: 42, arg2: custom")
    assert result == "Received 42 and custom"


def test_complex_device():
    device = DeviceComplex('test')
    result = device.parseCommand("store_data label: test, data: b'hello'")
    assert result == 5
    assert device.data['test'] == b'hello'


def test_single_subparser():

    session = SessionBase()

    result = session.parseCommand("mainInterface.add_numbers a: 2, b: 3")
    assert result == 5



def test_nested_commands_with_include_name():
    @commandParser(subparsers=['devices'], include_subparser_name=True)
    class InterfaceWithNames:
        def __init__(self, name: str):
            self.name = name
            self.devices: Dict[str, DeviceBase] = {}
            
        def add_device(self, device):
            self.devices[device.name] = device
            
    interface = InterfaceWithNames('test_interface')
    device = DeviceBase('test_device')
    interface.add_device(device)
    
    # With include_subparser_name=True, we need to include 'devices' in the path
    result = interface.parseCommand("devices.test_device.test_command arg1: 42")
    assert result == "Received 42 and default"

def test_bytes_conversion_2():

    @commandParser
    class DeviceBytesProcessor:
        def __init__(self, name: str):
            self.name = name
            self.data = {}
            
        @command
        def handleBytes(self, data: bytes):
            return data
    
    device = DeviceBytesProcessor('test')
    result = device.parseCommand("handleBytes data: b'hello'")
    assert result == b'hello'

    result = device.parseCommand("handleBytes data: [0x01 ,0x02 ,0x03]")
    assert result == b'\x01\x02\x03'

    result = device.parseCommand("handleBytes data: 0x01 0x02 0x03")
    assert result == b'\x01\x02\x03'

    result = device.parseCommand("handleBytes data: hello world")
    assert result == b'hello world'



def test_nested_commands_without_include_name():
    @commandParser(subparsers=['devices'])  # Default is include_subparser_name=False
    class InterfaceWithoutNames:
        def __init__(self, name: str):
            self.name = name
            self.devices: Dict[str, DeviceBase] = {}
            
        def add_device(self, device):
            self.devices[device.name] = device
            
    interface = InterfaceWithoutNames('test_interface')
    device = DeviceBase('test_device')
    interface.add_device(device)
    
    # Without include_subparser_name=True, we can skip 'devices' in the path
    result = interface.parseCommand("test_device.test_command arg1: 42")
    assert result == "Received 42 and default"

def test_inheritance_support():
    @commandParser
    class BaseDevice:
        def __init__(self, name: str):
            self.name = name
            
        @command()
        def base_command(self, arg: int) -> str:
            return f"Base {arg}"
    
    @commandParser
    class DerivedDevice(BaseDevice):
        @command()
        def derived_command(self, arg: int) -> str:
            return f"Derived {arg}"
    
    device = DerivedDevice('test')
    
    # Should be able to call both base and derived commands
    result = device.parseCommand("base_command 42")
    assert result == "Base 42"
    
    result = device.parseCommand("derived_command 43")
    assert result == "Derived 43"

def test_subparser_inheritance():
    @commandParser
    class BaseDevice:
        def __init__(self, name: str):
            self.name = name
            
        @command()
        def base_command(self, arg: int) -> str:
            return f"Base {arg}"
    
    @commandParser
    class DerivedDevice(BaseDevice):
        def __init__(self, name: str):
            super().__init__(name)

            
        @command()
        def derived_command(self, arg: int) -> str:
            return f"Derived {arg}"

    @commandParser(subparsers=['devices'])
    class Interface:
        def __init__(self):
            self.devices = {
                'dev1': DerivedDevice('dev1')
            }
    
    interface = Interface()
    
    # Test accessing base command through inheritance
    result = interface.parseCommand("dev1.base_command 42")
    assert result == "Base 42"
    
    # Test accessing derived command
    result = interface.parseCommand("dev1.derived_command 43")
    assert result == "Derived 43"
    
    # Test accessing nested subdevice
    result = interface.parseCommand("dev1.base_command 44")
    assert result == "Base 44"

def test_dynamic_subparser_modification():
    @commandParser(subparsers=['subdevices'])
    class DynamicDevice:
        def __init__(self, name: str):
            self.name = name
            self.subdevices = {}
            
        @command()
        def add_subdevice(self, name: str) -> str:
            self.subdevices[name] = DynamicDevice(name)
            return f"Added {name}"
            
        @command()
        def echo(self, msg: str) -> str:
            return f"{self.name}: {msg}"
    
    device = DynamicDevice('root')
    
    # Add a subdevice
    result = device.parseCommand("add_subdevice test")
    assert result == "Added test"
    
    # Should be able to use the newly added subdevice
    result = device.parseCommand("test.echo hello")
    assert result == "test: hello"

def test_override_command():
    @commandParser
    class BaseDevice:
        def __init__(self, name: str):
            self.name = name
            
        @command()
        def echo(self, msg: str) -> str:
            return f"Base: {msg}"
    
    @commandParser
    class DerivedDevice(BaseDevice):
        @command()
        def echo(self, msg: str) -> str:
            return f"Derived: {msg}"
    
    device = DerivedDevice('test')
    
    # Should use the overridden command
    result = device.parseCommand("echo hello")
    assert result == "Derived: hello"

def test_sub_class_command_with_inheritance():

    @commandParser(subparsers=['devices'])
    class InterfaceWithSub:
        def __init__(self, name: str):
            self.name = name
            self.devices: Dict[str, DeviceBase] = {}
            
        def add_device(self, device):
            self.devices[device.name] = device

    device = DeviceSub('test')
    interface = InterfaceWithSub('test_interface')

    interface.add_device(device)

    result = interface.parseCommand("test.test_command arg1: 42")
    assert result == "Received 42 and default"


def test_eval_expression(setup_session):
    session = setup_session
    result = session.parseCommand("test_interface.add_numbers a: $(2 * 3), b: $(5 + 5)")
    assert result == 16

def test_completion_tree(setup_session):
    session = setup_session
    tree = session.getCompletionTree()
    
    # Verify structure with new metadata format
    assert 'type' in tree
    assert tree['type'] == 'parser'
    assert 'children' in tree
    assert 'test_interface' in tree['children']
    assert tree['children']['test_interface']['type'] == 'parser'
    assert 'test_device' in tree['children']['test_interface']['children']
    assert 'add_numbers' in tree['children']['test_interface']['children']
    assert tree['children']['test_interface']['children']['add_numbers']['type'] == 'command'
    
    # Check parameter structure
    add_numbers_children = tree['children']['test_interface']['children']['add_numbers']['children']
    assert add_numbers_children['a']['type'] == 'parameter'
    assert add_numbers_children['a']['children'] == [1,2,3,4,5]
    assert add_numbers_children['b']['type'] == 'parameter' 
    assert add_numbers_children['b']['children'] == [0,1738]

def test_completions(setup_session):
    session = setup_session
    
    # Test root level completion - now returns tuples
    completions = session.getCompletions("")
    completion_names = [c[0] for c in completions]
    completion_types = [c[1] for c in completions]
    assert 'test_interface' in completion_names
    assert 'parser' in completion_types
    
    # Test nested completion
    completions = session.getCompletions("test_interface.")
    completion_names = [c[0] for c in completions]
    assert 'test_device' in completion_names
    assert 'add_numbers' in completion_names
    
    # Test command parameter completion
    completions = session.getCompletions("test_interface.add_numbers ")
    completion_names = [c[0] for c in completions]
    completion_types = [c[1] for c in completions]
    assert '5' in completion_names
    assert 'a' in completion_names
    assert 'b' in completion_names
    assert 'value' in completion_types
    assert 'parameter' in completion_types

    # Test positional lambda completion
    completions = session.getCompletions("test_interface.sub_numbers ")
    completion_names = [c[0] for c in completions]
    assert '1738' in completion_names
    assert 'a' in completion_names

    # Test command with some parameters
    completions = session.getCompletions("test_interface.add_numbers a: 5 , ")
    completion_names = [c[0] for c in completions]
    assert 'b' in completion_names
    assert '1738' in completion_names
    assert 'a' not in completion_names

    # Test command with some parameters
    completions = session.getCompletions("test_interface.add_numbers a: 5, b")
    completion_names = [c[0] for c in completions]
    assert 'b' in completion_names
    assert '1738' not in completion_names
    assert 'a' not in completion_names

    #Test args - now returns tuples
    completions = session.getCompletions("test_interface.add_numbers a:")
    expected_tuples = [('1', 'value'), ('2', 'value'), ('3', 'value'), ('4', 'value'), ('5', 'value')]
    assert expected_tuples == completions

    # Test with weird spacing
    completions = session.getCompletions("test_interface.add_numbers a:5,")
    completion_names = [c[0] for c in completions]
    assert 'b' in completion_names
    assert 'a' not in completion_names

def test_invalid_commands(setup_session):
    session = setup_session
    
    # Test invalid command path
    with pytest.raises(ValueError):
        session.parseCommand("invalid.path")
    
    # Test missing required argument
    with pytest.raises(ValueError):
        session.parseCommand("interfaces.test_interface.add_numbers")
    
    # Test invalid argument type
    with pytest.raises(ValueError):
        session.parseCommand("interfaces.test_interface.add_numbers a: invalid, b: 5")

def test_eval_security():
    # Test that eval is disabled by default
    interface = InterfaceBase('test')
    
    # Should not evaluate expression without allow_eval=True and raise exception

    try :
        result = interface.parseCommand("add_numbers a: $(2 * 3), b: 5")
        assert False
    except Exception as e:
        assert True 


def test_type_exceptions():
    device = DeviceBase('test')
    
    # should raise exception for invalid type
    try:
        result = device.parseCommand("test_command arg1: '42'")
        assert False
    except Exception as e:
        assert True


def test_bytes_conversion():
    device = DeviceComplex('test')
    
    # Test bytes conversion
    result = device.parseCommand("store_data label: test, data: b'hello'")
    assert isinstance(device.data['test'], bytes)
    assert device.data['test'] == b'hello'

    # Test hex conversion
    result = device.parseCommand("store_data label: test, data: 0x01 0x02 0x03")
    assert isinstance(device.data['test'], bytes)
    assert device.data['test'] == b'\x01\x02\x03'
    
def test_positional_arguments():
    device = DeviceBase('test')
    # Test with only positional arguments
    result = device.parseCommand("test_command 42")
    assert result == "Received 42 and default"
    
    # Test with both positional and keyword arguments
    result = device.parseCommand("test_command 42, arg2: custom")
    assert result == "Received 42 and custom"
    
    # Test with all arguments as positional
    result = device.parseCommand("test_command 42, custom")
    assert result == "Received 42 and custom"

def test_complex_device_positional():
    device = DeviceComplex('test')
    # Test with positional arguments
    result = device.parseCommand("store_data test, b'hello'")
    assert result == 5
    assert device.data['test'] == b'hello'
    
    # Test with mixed positional and keyword arguments
    result = device.parseCommand("store_data test, data: b'world'")
    assert result == 5
    assert device.data['test'] == b'world'

def test_invalid_positional_arguments():
    device = DeviceBase('test')
    
    # Test too many positional arguments
    with pytest.raises(ValueError, match="Too many positional arguments provided"):
        device.parseCommand("test_command 42, custom, extra")
    
    # Test missing required argument
    with pytest.raises(ValueError, match="Missing required argument"):
        device.parseCommand("test_command")
    
    # Test invalid type for positional argument
    with pytest.raises(ValueError):
        device.parseCommand("test_command invalid")



def test_complex_strings():

    @commandParser
    class DeviceStringProcessor:
        def __init__(self, name: str):
            self.name = name
            self.data = {}
            
        @command
        def handleString(self, cmd: str):
            return cmd
    
    device = DeviceStringProcessor('test')
    result = device.parseCommand('handleString main(1,"Hello World")')
    assert result == 'main(1,"Hello World")'

    result = device.parseCommand('handleString strcpy(argv[0],buf)')
    assert result == 'strcpy(argv[0],buf)'

def test_all_bytes_formats():
    """Test all supported bytes input formats"""
    
    @commandParser
    class BytesTestDevice:
        def __init__(self, name: str):
            self.name = name
            
        @command
        def test_bytes(self, data: bytes):
            return data
    
    device = BytesTestDevice('test')
    
    # Test all supported formats
    test_cases = [
        ("b'hello'", b'hello'),                    # Python byte literal with single quotes
        ('b"hello"', b'hello'),                    # Python byte literal with double quotes
        ("[0,1,2,3]", b'\x00\x01\x02\x03'),      # List of decimal values
        ("[0x00, 0x01, 0xFE]", b'\x00\x01\xFE'), # List of hex values
        ("00 01 02 FE", b'\x00\x01\x02\xFE'),    # Hex bytes separated by spaces
        ("0x000102FE", b'\x00\x01\x02\xFE'),     # Single hex string with 0x prefix
        ("0x01 0x02 0x03", b'\x01\x02\x03'),     # Hex bytes with 0x prefix and spaces
        ("plain text", b'plain text'),            # Plain text (UTF-8 encoded)
    ]
    
    for input_format, expected in test_cases:
        result = device.parseCommand(f"test_bytes data: {input_format}")
        assert result == expected, f"Format '{input_format}' failed: got {result}, expected {expected}"

@commandParser
class mySubParser:
    def __init__(self, name: str):
        self.name = name
        
    @command(help="Sub command")
    def sub_command(self, arg1: int):
        return f"Sub command received {arg1}"


@commandParser(flat=True, subparsers=['device'])
class CollapsedParser:
    def __init__(self, name: str):
        self.name = name
        self.device = mySubParser('test_device')

def test_collapsed_subparser():


    parser = CollapsedParser('test_interface')
    # Test accessing the subparser directly
    result = parser.parseCommand("sub_command arg1: 42")
    assert result == "Sub command received 42"

def test_collapsed_completions():
    parser = CollapsedParser('test_interface')
    
    # Test root level completion - now returns tuples
    completions = parser.getCompletions("")
    completion_names = [c[0] for c in completions]
    assert 'sub_command' in completion_names
    
    # Test command parameter completion
    completions = parser.getCompletions("sub_command ")
    completion_names = [c[0] for c in completions]
    assert 'arg1' in completion_names

    # Test with some parameters
    completions = parser.getCompletions("sub_command arg1: 42, ")
    completion_names = [c[0] for c in completions]
    assert 'arg1' not in completion_names



if __name__ == '__main__':
    pytest.main([__file__])