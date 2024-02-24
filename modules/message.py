from pyjosa.josa import Josa

def numberJosa(number: int) -> str:
	strList = { '1': '일', '2': '이', '3': '삼', '4': '사', '5': '오',
					'6': '육', '7': '칠', '8': '팔', '9': '구', '0': '십' }
	josa = Josa.get_josa(f"{strList[str(number).strip()[-1]]}", "을")
	return josa