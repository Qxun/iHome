#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '�������ʺ�'

#���ʺ�Token
accountToken= '�������ʺ�Token'

#Ӧ��Id
appId='����Ӧ��ID'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'

  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id
class CCP(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            obj = super(CCP, cls).__new__(cls, *args, **kwargs)
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls._instance = obj

        return cls._instance

    def send_template_sms(self, to, datas, tempId):

    
        #��ʼ��REST SDK
        result = self.rest.sendTemplateSMS(to,datas,tempId)
        if result.get('statusCode') == '000000':
            return 1
        else:
            return 0

#sendTemplateSMS(�ֻ�����,��������,ģ��Id)