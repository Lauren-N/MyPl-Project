"""
Implementation of the MyPL Virtual Machine (VM).

NAME: Lauren Nguyens
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_error import *
from mypl_opcode import *
from mypl_frame import *
import math


class VM:

    def __init__(self):
        # Creates a VM
        self.struct_heap = {}        # id -> dict
        self.array_heap = {}         # id -> list
        self.next_obj_id = 2024      # next available object id (int)
        self.frame_templates = {}    # function name -> VMFrameTemplate
        self.call_stack = []         # function call stack

    
    def __repr__(self):
        # Returns a string representation of frame templates.
        s = ''
        for name, template in self.frame_templates.items():
            s += f'\nFrame {name}\n'
            for i in range(len(template.instructions)):
                s += f'  {i}: {template.instructions[i]}\n'
        return s

    
    def add_frame_template(self, template):
        """Add the new frame info to the VM. 

        Args: 
            frame -- The frame info to add.

        """
        self.frame_templates[template.function_name] = template

    
    def error(self, msg, frame=None):
        """Report a VM error."""
        if not frame:
            raise VMError(msg)
        pc = frame.pc - 1
        instr = frame.template.instructions[pc]
        name = frame.template.function_name
        msg += f' (in {name} at {pc}: {instr})'
        raise VMError(msg)

    
    #----------------------------------------------------------------------
    # RUN FUNCTION
    #----------------------------------------------------------------------
    
    def run(self, debug=False):
        """Run the virtual machine."""

        # grab the "main" function frame and instantiate it
        if not 'main' in self.frame_templates:
            self.error('No "main" functrion')
        frame = VMFrame(self.frame_templates['main'])
        self.call_stack.append(frame)

        # run loop (continue until run out of call frames or instructions)
        while self.call_stack and frame.pc < len(frame.template.instructions):
            # get the next instruction
            instr = frame.template.instructions[frame.pc]
            # increment the program count (pc)
            frame.pc += 1
            # for debugging:
            if debug:
                print('\n')
                print('\t FRAME.........:', frame.template.function_name)
                print('\t PC............:', frame.pc)
                print('\t INSTRUCTION...:', instr)
                val = None if not frame.operand_stack else frame.operand_stack[-1]
                print('\t NEXT OPERAND..:', val)
                cs = self.call_stack
                fun = cs[-1].template.function_name if cs else None
                print('\t NEXT FUNCTION..:', fun)

            #------------------------------------------------------------
            # Literals and Variables
            #------------------------------------------------------------

            if instr.opcode == OpCode.PUSH:
                frame.operand_stack.append(instr.operand)

            elif instr.opcode == OpCode.POP:
                frame.operand_stack.pop()
            
            elif instr.opcode == OpCode.STORE:
                address = instr.operand
                value = frame.operand_stack.pop()

                while len(frame.variables) <= address:
                    frame.variables.append(None)
                frame.variables[address] = value
            
            elif instr.opcode == OpCode.LOAD:
                address = instr.operand
                value = frame.variables[address]
                frame.operand_stack.append(value)
            
            #------------------------------------------------------------
            # Operations
            #------------------------------------------------------------

            elif instr.opcode == OpCode.ADD:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None:
                    self.error("Cannot add null values")
                instr.operand = y + x
                frame.operand_stack.append(instr.operand)

            
            elif instr.opcode == OpCode.SUB:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None:
                    self.error("Cannot sub null values")
                instr.operand = y - x
                frame.operand_stack.append(instr.operand)

            
            elif instr.opcode == OpCode.MUL:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None:
                    self.error("Cannot mul null values")
                instr.operand = y * x
                if type(x) == int and type(y) == int:
                    instr.operand = math.floor(instr.operand)
                frame.operand_stack.append(instr.operand)
            
            
            elif instr.opcode == OpCode.DIV:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None:
                    self.error("Cannot div null values")
                if x == 0:
                    self.error("No division by 0")
                instr.operand = y / x
                if type(x) == int and type(y) == int:
                    instr.operand = math.floor(instr.operand)
                frame.operand_stack.append(instr.operand)
            
            elif instr.opcode == OpCode.AND:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None:
                    self.error("Cannot compare null values")
                check = x and y
                if check:
                    instr.operand = 'true'
                else:
                    instr.operand = 'false'
                frame.operand_stack.append(instr.operand)

            elif instr.opcode == OpCode.OR:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None:
                    self.error("Cannot compare null values")
                check = x or y
                if check:
                    instr.operand = 'true'
                else:
                    instr.operand = 'false'
                frame.operand_stack.append(instr.operand)

            elif instr.opcode == OpCode.NOT:
                x = frame.operand_stack.pop()
                if x == None:
                    self.error("Cannot compare null values")
                check = not x
                if check:
                    instr.operand = 'true'
                else:
                    instr.operand = 'false'
                frame.operand_stack.append(instr.operand)
            
            elif instr.opcode == OpCode.CMPLT:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None:
                    self.error("Cannot compare null values")
                check = y < x
                if check:
                    instr.operand = 'true'
                else:
                    instr.operand = 'false'
                frame.operand_stack.append(instr.operand)
            
            elif instr.opcode == OpCode.CMPLE:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if y == None or x == None:
                    self.error("Cannot compare null values")
                check = y <= x
                if check:
                    instr.operand = 'true'
                else:
                    instr.operand = 'false'
                frame.operand_stack.append(instr.operand)
            
            elif instr.opcode == OpCode.CMPEQ:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                check = y == x
                if check:
                    instr.operand = 'true'
                else:
                    instr.operand = 'false'
                frame.operand_stack.append(instr.operand)
            
            elif instr.opcode == OpCode.CMPNE:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                check = y != x
                if check:
                    instr.operand = 'true'
                else:
                    instr.operand = 'false'
                frame.operand_stack.append(instr.operand)

            #------------------------------------------------------------
            # Branching
            #------------------------------------------------------------

            elif instr.opcode == OpCode.JMP:
                # setting the frame pc to the given instr.operand
                frame.pc = instr.operand
            
            elif instr.opcode == OpCode.JMPF:
                x = frame.operand_stack.pop()

                # if x is python false OR MyPL false
                if x == False or x == 'false':
                    frame.pc = instr.operand
            #------------------------------------------------------------
            # Functions
            #------------------------------------------------------------
            elif instr.opcode == OpCode.RET:

                # getting return val from operand_stack
                return_val = frame.operand_stack.pop()

                # popping the call of the call stack
                self.call_stack.pop()

                # as long as there is something in the call stack, change frame to new fun
                if len(self.call_stack) != 0:
                    frame = self.call_stack[-1]
                
                # add return value
                frame.operand_stack.append(return_val)

            elif instr.opcode == OpCode.CALL:
                # getting function name from stack
                fun_name = instr.operand

                # creating new frame
                new_frame_template = self.frame_templates[fun_name]

                # instantating a new frame
                new_frame = VMFrame(new_frame_template)

                # append new frame to the call stack list
                self.call_stack.append(new_frame)

                # run through arguements
                for i in range (0,new_frame_template.arg_count):
                    arg = frame.operand_stack.pop()
                    new_frame.operand_stack.append(arg)

                # setting curr frame to the new frame
                frame = new_frame
            #------------------------------------------------------------
            # Built-In Functions
            #------------------------------------------------------------

            elif instr.opcode == OpCode.TODBL:
                x = frame.operand_stack.pop()
                try:
                    double_val = float(x)
                    frame.operand_stack.append(double_val)
                except (TypeError, ValueError):
                    self.error(f'Cant convert {x} to a double')
            
            elif instr.opcode == OpCode.TOINT:
                x = frame.operand_stack.pop()
                try:
                    int_val = int(x)
                    frame.operand_stack.append(int_val)
                except (TypeError, ValueError):
                    self.error(f'Cant convert {x} to a int')
            
            elif instr.opcode == OpCode.TOSTR:
                x = frame.operand_stack.pop()
                if x == None:
                    self.error("Null can not be turned into a string")
                try:
                    string_val = str(x)
                    frame.operand_stack.append(string_val)
                except (TypeError, ValueError):
                    self.error(f'Cant convert {x} to a string')

            elif instr.opcode == OpCode.LEN:
                x = frame.operand_stack.pop()
                if x == None:
                    self.error("None has no length")
                if type(x) == str:
                    frame.operand_stack.append(len(x))
                else:
                    obj = self.array_heap
                    frame.operand_stack.append(len(obj[x]))
            
            elif instr.opcode == OpCode.GETC:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()

                # type checking
                if type(x) != str or x == None:
                    self.error("get requires a string")

                # ensuring index syntax is correct
                if y == None or y < 0 or y >= len(x):
                    self.error("Appropriate index required")
                
                # appending character to the operand stack
                frame.operand_stack.append(x[y])

            #------------------------------------------------------------
            # Heap
            #------------------------------------------------------------

            elif instr.opcode == OpCode.ALLOCS:
                # saving new OID
                oid = self.next_obj_id

                # incrementing
                self.next_obj_id += 1

                # setting up new struct to oid
                self.struct_heap[oid] = {}

                # appending oid to operand stack
                frame.operand_stack.append(oid)
            
            elif instr.opcode == OpCode.SETF:
                a = instr.operand
                x = frame.operand_stack.pop()
                if x == None:
                    self.error("Object location can not be null")
                oid_y = frame.operand_stack.pop()
                if oid_y == None:
                    self.error("Object location can not be null")

                # getting object from struct heap list
                obj = self.struct_heap

                # getting field object from oid and x
                obj[oid_y][a] = x

                # resetting struct heap
                self.struct_heap = obj
            
            elif instr.opcode == OpCode.GETF:
                a = instr.operand
                x_oid = frame.operand_stack.pop()
                if x_oid == None:
                    self.error("Object location can not be null")
                
                # creating copy of struct heap
                value = self.struct_heap

                # appending field gotten to operand stack
                frame.operand_stack.append(value[x_oid][a])
            
            elif instr.opcode == OpCode.ALLOCA:
                # setting up new oid
                oid = self.next_obj_id
                if oid == None:
                    self.error("Array location must be valid")
                self.next_obj_id += 1
                array_length = frame.operand_stack.pop()
                if array_length == None or array_length < 0:
                    self.error("Appropriate Array Length must be defined")
                # ... check for valid array length value ...
                self.array_heap[oid] = [None for _ in range (array_length)]
                frame.operand_stack.append(oid)
        
            elif instr.opcode == OpCode.SETI:
                x_val = frame.operand_stack.pop()
                y_index = frame.operand_stack.pop()
                z_oid = frame.operand_stack.pop()
                if x_val == None or y_index == None or z_oid == None:
                    self.error("Incorrect array set syntax")
                if type(y_index) != int:
                    self.error("Array index must equal integer")
                if y_index < 0 or y_index >= len(self.array_heap[z_oid]):
                    self.error("Out of bound array indexing")

                # setting array in array heap at z oid and y index to x_val from operand stack
                self.array_heap[z_oid][y_index] = x_val
            
            elif instr.opcode == OpCode.GETI:
                x_index = frame.operand_stack.pop()
                y_oid = frame.operand_stack.pop()
                if x_index == None or y_oid == None:
                    self.error("Incorrect array set syntax")
                if x_index < 0 or x_index >= len(self.array_heap[y_oid]):
                    self.error("Out of bound array indexing")

                # getting value from array at oid at x index
                value = self.array_heap[y_oid][x_index]

                # appending to opperand stack
                frame.operand_stack.append(value)
            
            #------------------------------------------------------------
            # Special 
            #------------------------------------------------------------

            elif instr.opcode == OpCode.DUP:
                x = frame.operand_stack.pop()
                frame.operand_stack.append(x)
                frame.operand_stack.append(x)

            elif instr.opcode == OpCode.NOP:
                # do nothing
                pass
            
            elif instr.opcode == OpCode.WRITE:
                x = frame.operand_stack.pop()
                if x == None:
                    x = 'null'
                print(x, end='')
            
            elif instr.opcode == OpCode.READ:
                x = input()
                frame.operand_stack.append(x)

            else:
                self.error(f'unsupported operation {instr}')

        
