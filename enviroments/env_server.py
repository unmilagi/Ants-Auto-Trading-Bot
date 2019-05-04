# -*- coding: utf-8 -*-
import logging
import consts
import json
import sys

from messenger.q_publisher import MQPublisher
from exchangem.model.coin_model import CoinModel

class BaseClass():
	pass

class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]
		
class Enviroments(BaseClass, metaclass=Singleton):
    """
    모든 설정을 여기서 메모리에 들고 있으면서 관리한다
    모든 설정은 파일에 기록될 때 ants.conf를 제외하고 모두 암호화 된다.
    설정 값을 입력할 때도 cli를 통해서 설정한다. 더 이상 파일을 직접 수정한 설정은 없다
    설정 값 중 키 값은 암호화 되지 않는다. 값 부분만 모두 암호화 된다.
    
    대표적 기록 값
    - 프로젝트 경로
    - 거래소 데이터
    - 각종 큐 경로
    """
    DEFAULT_CONF='configs/ants.conf'
    AUTO_CONF='configs/ant_auto.conf'
    
    #구동 시스템에 관한 정보
    sys = {}
    common = {}
    exchanges = {}
    strategies = {}
    messenger = {}
    qsystem = {}
    #사용자가 지정한 트레이딩 대상 코인을 지정함
    trading = {}
    etc = {}
    
    init_load = True
    
    def __init__(self, args={}):
        self.logger = logging.getLogger(__name__)
        self.first_exception = True

    def __repr__(self):
        return str(dict(self))
        
    def from_dict(self, src):
        if(type(src) is not type({})):
            return
        
        for a, b in src.items():
            setattr(self, a, b)
            print('a:{}\tb:{}'.format(a,b))
        
    def __iter__(self):
        klass = self.__class__    
        iters = dict((x,y) for x,y in klass.__dict__.items() if x[:2] != '__' and not callable(y))

        iters.update(self.__dict__)

        exclucive=['AUTO_CONF', 'DEFAULT_CONF', 'logger', 'init_load', 'first_exception']
        for x,y in iters.items():
            if(x not in exclucive):
                yield x,y

    def save_config(self, file_name=None):
        if(file_name is None):
            file_name = self.AUTO_CONF

        with open(file_name, 'w') as file:
            file.write(json.dumps(dict(self), indent=4, sort_keys=True)) # use `json.loads` to do the reverse

    def load_config(self, file_name=None):
        if(file_name is None):  
            file_name = self.AUTO_CONF
            
        self.logger.debug('file_name : {}'.format(file_name))
        try:
            with open(file_name, 'r') as file:
                rdict = json.loads(file.read())
                self.from_dict(rdict)
                self.logger.debug('rdict : {}'.format(type(rdict)))
        except Exception as e:
            if(self.first_exception):
                self.first_exception = False
                self.logger.info('Can''t load auto config. Will load default config : {}'.format(e))
                
                if(self.load_config_ver1(self.DEFAULT_CONF)):
                    self.set_default()
                    self.save_config()
                    return
                else:
                    self.load_config(self.DEFAULT_CONF)
            else:
                self.logger.error('Can''t load default config. : {}'.format(e))
                sys.exit(1)
        
        self.set_default()
        
    def set_default(self):
        #초기값이 반드시 있어야하는 변수들을 여기서 선언한다
        if(Enviroments().etc.get('test_mode') is None):
            Enviroments().etc['test_mode'] = 'True'
        
        if(Enviroments().exchanges.get('default') is None):
            coin = CoinModel()
            coin.amount.available = 1000
            coin.amount.keep = 0
            
            keys = {
                'apiKey':'',
                'secret':''
            }
            trading_list = {
                'all' : True,
                'list' : []
            }
            default_setting = {
                'coin' : dict(coin),
                'keys' : keys,
                'traing_list' : trading_list
            }
            
            Enviroments().exchanges['default'] = default_setting
        
    def load_config_ver1(self, file_name):
        """
        구버젼 config 포멧을 읽어들인다
        구버젼이면 True, 아니면 False를 리턴한다
        """
        try:
            with open(file_name, 'r') as file:
                rdict = json.loads(file.read())
                self.logger.debug(rdict['key_file']['rsa_key_file'])
                item = {
                    'common':rdict
                }
                self.from_dict(item)
                self.logger.debug('load config version 1 : {}'.format(item))
        except Exception as e:
            self.logger.debug('exception : {}'.format(e))
            return False
        
        return True
    
if __name__ == '__main__':
    print('Enviroments test')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    Enviroments().load_config()
    
    en1 = Enviroments()
    en2 = Enviroments()
    
    en1.common['ssh_pub'] = '~\pi\.ssh\id_rsa.pub'
    
    print(dict(en1))
    
    f_name = 'test_conf.tmp'
    en1.save_config(f_name)
    
    en1.load_config(f_name)
    
    en1.from_dict
    
    print(dict(en1))
    
    # print(consts.ENV)
    # print(en1)
    # print(en1.common)
    # print(en2.common)

    # dt = vars(en1)
    # print(dt)

    # j = en1.to_json()
    # print(j)
    
    # en1.from_json(j)