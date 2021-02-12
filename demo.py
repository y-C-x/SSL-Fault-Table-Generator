#!/usr/bin/env python3

# Written by Chengxin Yu @ Feb 12, 2021
# SSL Fault Table Generator.
# Type in digital rules for the ciruit in the file called 'rules'.
# Only simulates for simple digital logic. Complex logic like gate fault in cmos structure is not supported yet.

# View Setting
USE_XV = 0
USE_X = 1

# read rules
rule_fileName = "rules"
rules = open(rule_fileName, "r")
inputs = []
wires = []
outputs = []
logics = []

subIn = 0
subOut = 0
subLog = 0
subWire = 0

for lines in rules:
    line = lines.rstrip() 
    
    if not line: # escape the empty lines
        continue   

    if 'inputs' in line:
        subIn = 1
        subOut = 0
        subLog = 0
        subWire = 0
        continue 
    
    if 'wires' in line:
        subWire = 1
        subOut = 0
        subIn = 0
        subLog = 0
        continue

    if 'outputs' in line:
        subOut = 1
        subIn = 0
        subLog = 0
        subWire = 0
        continue

    if 'logics' in line:
        subLog = 1
        subOut = 0
        subIn = 0
        subWire = 0
        continue
        
    if (subIn == 1):
        inputs += line.split()
    if (subWire == 1):
        wires += line.split()
    if (subOut == 1):
        outputs += line.split()
    if (subLog == 1):
        logics.append(line)
    
rules.close()

# print("inputs:  ", inputs)
# print("wires:   ", wires)
# print("outputs: ", outputs)
# print("logics:  ", logics)

inputNum = len(inputs)
wireNum = len(wires)
outputNum = len(outputs)

# total ssl faults
ssl_num = inputNum + outputNum + wireNum
total_ssl_num = 2*ssl_num

# ssl fault name
ssl_vars = inputs + wires +  outputs
# print("total SSL fault: ", total_ssl_num)

ssl_Str = []
for fault_var in ssl_vars:
    ssl_Str.append(fault_var + '/0')
    ssl_Str.append(fault_var + '/1')
    
# print("SSL cases: ", ssl_Str)

testVectorNum = 2 ** inputNum
# print("total test num: ", testVectorNum)

formatStr = '#0{}b'.format(inputNum+2)

testVectors = []
for decNum in range(testVectorNum):
    testVector = tuple(int(i) for i in format(decNum, formatStr)[2:])
    testVectors.append(testVector)

# print(testVectors)

# inputVarStr = ''
# inputVarStr = " = 0\n".join(inputs)
# inputVarStr += ' = 0'
# print(inputVarStr)

# origFxStr = ''
# origFxStr = "\n".join(logics)
# print(origFxStr)

# loopStr = 'for testVector in testVectors:\n'
# loopStr += '\t{} = testVector\n'.format(','.join(inputs))
# loopStr += '\t{}\n'.format('\n\t'.join(logics))
# loopStr += '\tprint({})'.format(','.join(inputs))
# print(loopStr)

# print()


# exec(loopStr)
for output in outputs:
    print("FAULT TABLE FOR OUTPUT {}".format(output))
    print('{} | {} | '.format(' '.join(inputs), ' | '.join(output)), end='')
    print('{}'.format(' | '.join(ssl_Str)), end=' |\n')
    
    for testVector in testVectors:
        print('{} | '.format(' '.join([str(i) for i in testVector])), end='')
        for inVar in inputs:
            exec("{} = testVector".format(','.join(inputs)))
                
        for logic in logics:
            exec(logic)
            
        exec("{0}_orig = {0}".format(output))
            
        exec("print({} ,'| ', end='')".format(", '|', ".join(output)))
        
        for ssl_fault in ssl_Str:
            # print(ssl_fault)
            exec("{} = testVector".format(','.join(inputs)))
            for inVar in inputs:
                if (inVar in ssl_fault):
                    # print('{}={}'.format(inVar,ssl_fault[-1]))
                    exec('{}={}'.format(inVar,ssl_fault[-1]))

            for logic in logics:
                wireVar = logic.split(' ')[0]
                if(wireVar in ssl_fault):
                    # print('{}={}'.format(wireVar,ssl_fault[-1]))
                    exec('{}={}'.format(wireVar,ssl_fault[-1]))
                else:
                    # print(logic)
                    exec(logic)
    
            if(USE_XV):
                exec("if {0} != {0}_orig: print('x/{{}} | '.format({0}), end='')\nelse: print('  - | ', end='')".format(''.join(output)))
            elif (USE_X):
                exec("if {0} != {0}_orig: print(' x  | '.format({0}), end='')\nelse: print(' -  | ', end='')".format(''.join(output)))
            else:
                exec("print( ' {{}}  | '.format({}), end='')".format("".join(output)))
        print()
        
print("FAULT TABLE IN GENERAL")
print('{} | '.format(' '.join(inputs)), end='')
print('{}'.format(' | '.join(ssl_Str)), end=' |\n')
    
for testVector in testVectors:
    print('{} | '.format(' '.join([str(i) for i in testVector])), end='')
        
    for inVar in inputs:
        exec("{} = testVector".format(','.join(inputs)))
            
    for logic in logics:
        exec(logic)

    for output in outputs:            
        exec("{0}_orig = {0}".format(output))

    for ssl_fault in ssl_Str:
        exec("{} = testVector".format(','.join(inputs)))
        for inVar in inputs:
            if (inVar in ssl_fault):
                # print('{}={}'.format(inVar,ssl_fault[-1]))
                exec('{}={}'.format(inVar,ssl_fault[-1]))

        for logic in logics:
            wireVar = logic.split(' ')[0]
            if(wireVar in ssl_fault):
                # print('{}={}'.format(wireVar,ssl_fault[-1]))
                exec('{}={}'.format(wireVar,ssl_fault[-1]))
            else:
                # print(logic)
                exec(logic)
        
        for output in outputs:
            fault = eval("{0} != {0}_orig".format(''.join(output)))
            if fault:
                break
               
        if not fault:
            print(' -  | ', end='')
        else:
             print(' x  | ', end='')     
    print()