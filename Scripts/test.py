
# def twos_cmpl(n):
#     N = int(n,2)^int('ffff',16)
#     return '{:>16b}'.format(N+1)[-16:]

# def b_to_d(b):
#     if b[0] == '1':
#         n = twos_cmpl(b)
#         return -int(n,2)
#     else:
#         return int(b,2)

# def d_to_b(d):
#     N = abs(d)
#     n = '{:>016b}'.format(N)
#     if d < 0:
#         return twos_cmpl(n)
#     else:
#         return n
#---------------------------------------------------------

# c = '1'
# if c == '1':
#     print('done')
# else:
#     print('no')
#---------------------------------------------------------

# zvnc = ['0','0','0','0']
# Rn = -32768
# if Rn not in range(-32768,32768):
#         zvnc[1] = '1'
# print(zvnc)
#---------------------------------------------------------

def is_AC(x,y,c,b):
	if x < 0:
		x = 65536 + x
	if y < 0:
		y = 65536 + y
	if b == -1:
		b = 65535
	if x + y + c + b > 65535:
		return '1'
	else:
		return '0'
is_sub = '0'
C = '1'
print(is_AC(0,0,1,-(int(is_sub)&int(C))))


