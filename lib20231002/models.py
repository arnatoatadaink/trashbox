# import sqlalchemy.sql.sqltypes as satype
import sqlalchemy.dialects.mysql as mstype

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship

from typing import List

import os,sys
sys.path.append(os.environ["alembic_base"])
from settings import Base,Engine
    
class add_dataTINYBLOB(Base):
    __tablename__ = 'add_datatinyblob'
    
    data_settings_id    :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    data_id             :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_settings_id   :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_count         :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    data                :Mapped[bytes]   = mapped_column(mstype.TINYBLOB,nullable=True)
class add_dataBLOB(Base):
    __tablename__ = 'add_datablob'
    
    data_settings_id    :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    data_id             :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_settings_id   :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_count         :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    data                :Mapped[bytes]   = mapped_column(mstype.BLOB,nullable=True)
class add_dataMEDIUMBLOB(Base):
    __tablename__ = 'add_datamediumblob'
    
    data_settings_id    :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    data_id             :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_settings_id   :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_count         :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    data                :Mapped[bytes]   = mapped_column(mstype.MEDIUMBLOB,nullable=True)
class add_dataLONGLOB(Base):
    __tablename__ = 'add_datalongblob'
    
    data_settings_id    :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    data_id             :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_settings_id   :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_count         :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    data                :Mapped[bytes]   = mapped_column(mstype.LONGBLOB,nullable=True)
    
class class_set(Base):
    __tablename__ = 'class_set'
    
    class_settings_id   :Mapped[int]     = mapped_column(mstype.INTEGER,ForeignKey("class_settings.class_settings_id"),primary_key=True) # {'key': 'PRI'}
    # class_settings_id   :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True) # {'key': 'PRI'}
    class_id            :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True) # {'key': 'PRI'}
    class_key           :Mapped[str]     = mapped_column(mstype.VARCHAR(length=8))
    class_name          :Mapped[str]     = mapped_column(mstype.VARCHAR(length=32))

    class_settings : Mapped["class_settings"]   = relationship(back_populates="class_set",foreign_keys=class_settings_id)
    
class class_settings(Base):
    __tablename__ = 'class_settings'
    
    id   :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True,name="class_settings_id") # {'extra': 'auto_increment', 'key': 'PRI'}
    class_name          :Mapped[str]     = mapped_column(mstype.VARCHAR(length=32),nullable=True)
    adddata_columns     :Mapped[str]     = mapped_column(mstype.VARCHAR(length=1024),nullable=True)
    adddata_format      :Mapped[str]     = mapped_column(mstype.VARCHAR(length=256),nullable=True)
    adddata_length      :Mapped[int]     = mapped_column(mstype.INTEGER,nullable=True)
    detail              :Mapped[str]     = mapped_column(mstype.VARCHAR(length=1024),nullable=True)
    multi_class         :Mapped[int]     = mapped_column(mstype.TINYINT(1),default=0) # {'default': b'0'}
    single_class        :Mapped[int]     = mapped_column(mstype.TINYINT(1),default=0) # {'default': b'0'}
    no_class            :Mapped[int]     = mapped_column(mstype.TINYINT(1),default=0) # {'default': b'0'}
    multi_data          :Mapped[int]     = mapped_column(mstype.TINYINT(1),default=0) # {'default': b'0'}
    
    class_set : Mapped[List["class_set"]]   = relationship(back_populates="class_settings")
    
class data_set(Base):
    __tablename__ = 'data_set'
    
    data_settings_id    :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True) # {'key': 'PRI'}
    data_id             :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True) # {'key': 'PRI'}
    data_name           :Mapped[str]     = mapped_column(mstype.VARCHAR(length=255))
    batch_size          :Mapped[int]     = mapped_column(mstype.INTEGER,nullable=True)
    
class data_settings(Base):
    __tablename__ = 'data_settings'
    
    id    :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True,name="data_settings_id") # {'extra': 'auto_increment', 'key': 'PRI'}
    ref_func            :Mapped[str]     = mapped_column(mstype.VARCHAR(length=32))
    path                :Mapped[str]     = mapped_column(mstype.VARCHAR(length=255))
    options             :Mapped[str]     = mapped_column(mstype.VARCHAR(length=32),nullable=True)
    data_type           :Mapped[str]     = mapped_column(mstype.VARCHAR(length=32),nullable=True)
    batch_size          :Mapped[int]     = mapped_column(mstype.INTEGER,nullable=True)
    detail              :Mapped[str]     = mapped_column(mstype.VARCHAR(length=1024),nullable=True)
    
class dataclass_set(Base):
    __tablename__ = 'dataclass_set'
    
    data_settings_id    :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    data_id             :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_settings_id   :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_count         :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True, autoincrement=False) # {'key': 'PRI'}
    class_id            :Mapped[int]     = mapped_column(mstype.INTEGER,default=0) # {'default': b'0'}
    is_dissable         :Mapped[int]     = mapped_column(mstype.TINYINT(1),default=0) # {'default': b'0'}
    is_unknown          :Mapped[int]     = mapped_column(mstype.TINYINT(1),default=0) # {'default': b'0'}
    is_unset            :Mapped[int]     = mapped_column(mstype.TINYINT(1),default=0) # {'default': b'0'}

class multidata_set(Base):
    __tablename__ = 'multidata_set'
    
    data_settings_id    :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True) # {'key': 'PRI'}
    data_id             :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True) # {'key': 'PRI'}
    ref_data_settings_id:Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True) # {'key': 'PRI'}
    ref_data_id         :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True) # {'key': 'PRI'}
    
class logined_data(Base):
    __tablename__ = 'idu'
    
    # id      :Mapped[int]     = mapped_column(mstype.INTEGER,ForeignKey("oay.rbq"),primary_key=True,name="llz") # {'key': 'PRI'}
    id      :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True,name="llz") # {'key': 'PRI'}
    ip      :Mapped[str]     = mapped_column(mstype.VARCHAR(length=128),primary_key=True,name="bhe") # {'key': 'PRI'}
    iptype  :Mapped[str]     = mapped_column(mstype.VARCHAR(length=2),nullable=True,name="jfs")
    date    :Mapped[str]     = mapped_column(mstype.DATETIME,nullable=True,name="aa3")
    
    # user    :Mapped["user"]   = relationship(back_populates="logined_data",foreign_keys=id)
    
class user(Base):
    __tablename__ = 'oay'
    
    name           :Mapped[str]     = mapped_column(mstype.VARCHAR(length=32),index=True,name='wha') # {'key': 'UNI'}
    fullname       :Mapped[str]     = mapped_column(mstype.VARCHAR(length=64),nullable=True,name="iog")
    id             :Mapped[int]     = mapped_column(mstype.INTEGER,primary_key=True,name="rbq") # {'extra': 'auto_increment', 'key': 'PRI'}
    hashedpassword :Mapped[str]     = mapped_column(mstype.VARCHAR(length=60),name="axg")
    salt           :Mapped[str]     = mapped_column(mstype.VARCHAR(length=36),name="k96")
    address        :Mapped[str]     = mapped_column(mstype.VARCHAR(length=257),name="j9w")
    createdate     :Mapped[str]     = mapped_column(mstype.DATETIME,nullable=True,name="plc")
    updatedate     :Mapped[str]     = mapped_column(mstype.DATETIME,nullable=True,name="xyi")
    expired        :Mapped[str]     = mapped_column(mstype.DATETIME,nullable=True,name="ru2")
    flag           :Mapped[int]     = mapped_column(mstype.TINYINT(1),default=0,name="ge2")

    # logined_data   :Mapped[List["logined"]]   = relationship(back_populates="user")

# TODO
#   model implement scheme
#   deep / machine larning model
class model(Base):
    __tablename__ = "model"
    
    id      :Mapped[int] = mapped_column(mstype.INTEGER,primary_key=True)
    name    :Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    io      :Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    type    :Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    created :Mapped[str] = mapped_column(mstype.DATETIME)
    # 該当モデルの訓練済みパラメータ保存先
    # ここについて仕様の深堀が必要
    store_path:Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    # modelの基軸実装、これ以外に引き当てるパラメータ群を規定する
    # need switch enviroment
    module_name: Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    class_name: Mapped[str] = mapped_column(mstype.VARCHAR(length=256),nullable=True)
    func_name: Mapped[str] = mapped_column(mstype.VARCHAR(length=256),nullable=True)
    
class train_info(Base):
    __tablename__ = "train_info"

    id                :Mapped[int] = mapped_column(mstype.INTEGER,primary_key=True)
    model_id          :Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("model.id"))
    data_settings_id  :Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("data_settings.data_settings_id"))
    class_settings_id :Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("class_settings.class_settings_id"))
    train_settings_id :Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("train_settings.train_settings_id"))
    started           :Mapped[str] = mapped_column(mstype.DATETIME)
    traintime         :Mapped[str] = mapped_column(mstype.DATETIME)
    epoch             :Mapped[int] = mapped_column(mstype.INTEGER)
    train_type        :Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    test_type         :Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    
class score(Base):
    __tablename__ = "score"
    # TODO
    id : Mapped[int] = mapped_column(mstype.INTEGER,primary_key=True)
    train_id : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("train_info.id"))
    epoch:Mapped[int] = mapped_column(mstype.INTEGER)
    score: Mapped[float] = mapped_column(mstype.FLOAT)
    
class train_settings(Base):
    __tablename__ = "train_settings"
    
    id :Mapped[int] = mapped_column(mstype.INTEGER,primary_key=True,name="train_settings_id")
    train_pre_process_id  : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("process_list.id"),default=-1) # pre  process for input  data in training   start example augmentation
    train_post_process_id : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("process_list.id"),default=-1) # post process for output data in training   end   example output log
    test_pre_process_id   : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("process_list.id"),default=-1) # pre  process for input  data in validation start example augmentation
    test_post_process_id  : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("process_list.id"),default=-1) # post process for output data in validation end   example output log
    epoch_pre_process_id  : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("process_list.id"),default=-1) # pre  process for input  data in epoch      start
    epoch_post_process_id : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("process_list.id"),default=-1) # post process for output data in epoch      end   example loss metrics
    # fit_pre_process    # pre  process for input  data in batch start    example load data ? sequence ? inline ? call backs ?
    # fit_post_process   # post process for output data in batch end
    # loss_metrics_id       : Mapped[int] = mapped_column(mstype.INTEGER,default=-1,ForeignKey("process_list.id")) # post process for output data in epoch end      example loss metrics
    # train_type            : Mapped[str] = mapped_column(mstype.VARCHAR(length=256)) # use for machine learning,excample "cross validation"　nn model is split test only
    train_process         : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("process_list.id"),default=-1)
    test_process          : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("process_list.id"),default=-1)
    hyper_parameter_id    : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("parameters.id")  ,default=-1)
    
class process_list(Base):
    __tablename__ = "process_list"
    
    id         : Mapped[int] = mapped_column(mstype.INTEGER,primary_key=True)
    process_id : Mapped[int] = mapped_column(mstype.INTEGER,ForeignKey("process.id"),primary_key=True)
    name       : Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    
class process(Base):
    __tablename__ = "process"
    
    id          : Mapped[int] = mapped_column(mstype.INTEGER,primary_key=True)
    name        : Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    prefix      : Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    suffix      : Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    module_name : Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    class_name  : Mapped[str] = mapped_column(mstype.VARCHAR(length=256),nullable=True)
    func_name   : Mapped[str] = mapped_column(mstype.VARCHAR(length=256),nullable=True)

# TODO
#   id+typeをprimary_keyに変更し
#   役割と範囲を拡大する
#     １．selectorのparameter_listとして使う
#         typeをkeyにidの連番を取得しname:id、あるいはname:nameを提供する
#   blobの保存範囲について
#     事前の予定ではidに紐づく複数の子明細を引き当てる形を想定していた
#     page_parametersの類型で実装し
#     type/nameに所属するパラメータをjson_strのdictとして保持する
#   type
#     argment？
#     metrics？
#       これはargmentに含むのでは？
#     testtype？
#     model_structure
#       modelのfunc系に対する引数
#     parameters
#       複数typeのparameterを引き当てる型
class parameters(Base):
    __tablename__ = "parameters"
    
    type:Mapped[str]   = mapped_column(mstype.VARCHAR(length=32),primary_key=True)
    id  :Mapped[int]   = mapped_column(mstype.INTEGER,primary_key=True)
    name:Mapped[str]   = mapped_column(mstype.VARCHAR(length=32))
    # attr:Mapped[int]   = mapped_column(mstype.INTEGER,default=0) # これを使うイメージが沸かない
    enable:Mapped[int] = mapped_column(mstype.TINYINT(1),default=1)
    data:Mapped[bytes] = mapped_column(mstype.BLOB(length=65535))

class page_parameters(Base):
    __tablename__ = "page_parameters"
    
    id  :Mapped[int]   = mapped_column(mstype.INTEGER,primary_key=True)
    enable:Mapped[int] = mapped_column(mstype.TINYINT(1),default=1)
    data:Mapped[bytes] = mapped_column(mstype.BLOB(length=65535))
