
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


c = '1'
if c == '1':
    print('done')
else:
    print('no')