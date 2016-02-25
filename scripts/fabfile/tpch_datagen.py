from fabric.api import run,cd,parallel,serial
from fabric.contrib.files import exists
counter = 0

@parallel
def tpch_remove():
        if exists('/data/mdindex/yilu'):
            run('rm -rf /data/mdindex/yilu')

@parallel
def tpch_download():
        if not exists('/data/mdindex/yilu'):
            run('mkdir /data/mdindex/yilu')
        with cd('/data/mdindex/yilu'):
	    run('git clone https://github.com/electrum/tpch-dbgen.git')

	with cd('/data/mdindex/yilu/tpch-dbgen'):
	    run('make')

@serial
def tpch_script_gen_100():
    global counter
    try:
        if not exists('/data/mdindex/yilu/tpch100'):
            run('mkdir /data/mdindex/yilu/tpch100')

        with cd('/data/mdindex/yilu/tpch-dbgen'):
            try:
                # delete any old tables before creating new ones
                run('rm *tbl*')
            except:
                pass
            script = "#!/bin/bash\n"
            script += "cd /data/mdindex/yilu/tpch-dbgen/\n"
            cmd = './dbgen -s 100 -C 10 -S %d\n' % (counter + 1)
            script += cmd

            run('echo "%s" > data_gen.sh' % script)
            run('chmod +x data_gen.sh')
    except:
        pass

    counter += 1

@parallel
def tpch_gen_100():
    run('nohup /data/mdindex/yilu/tpch-dbgen/data_gen.sh >> /tmp/xxx 2>&1 < /dev/null &', pty=False)

@serial
def create_script_move_data():
    global counter
    with cd('/data/mdindex/yilu'):
        script = "#!/bin/bash\n"
        script += "/home/mdindex/hadoop-2.6.0/bin/hadoop fs -copyFromLocal " + \
            "/data/mdindex/yilu/tpch-dbgen/*.tbl.%d /user/yilu/tpch100-raw/" % (counter + 1)
        run('echo "%s" > move_data.sh' % script)
        run('chmod +x move_data.sh')

    counter += 1


@parallel
def move_data():
    run('nohup /data/mdindex/yilu/move_data.sh >> /tmp/xxx 2>&1 < /dev/null &', pty=False)

@parallel
def create_script_stop_dbgen():
    with cd('/data/mdindex/yilu'):
        script = "#!/bin/bash\n"
        script += "pkill dbgen" 
        run('echo "%s" > stop_dbgen.sh' % script)
        run('chmod +x stop_dbgen.sh')

@parallel
def stop_dbgen():
    run('nohup /data/mdindex/yilu/stop_dbgen.sh >> /tmp/xxx 2>&1 < /dev/null &', pty=False)

@parallel
def create_script_clear_tmp():
    if not exists('/data/mdindex/yilu'):
        run('mkdir /data/mdindex/yilu')
    with cd('/data/mdindex/yilu'):
        script = "#!/bin/bash\n"
        script += "rm -rf /tmp/*" 
        script += "rm -rf /tmp/xxx" 
        run('echo "%s" > clear_tmp.sh' % script)
        run('chmod +x clear_tmp.sh')

@parallel
def clear_tmp():
    run('nohup /data/mdindex/yilu/clear_tmp.sh >> /tmp/xxx 2>&1 < /dev/null &', pty=False)



@serial
def create_script_download_data():
    if exists('/data/mdindex/yilu/tpch100'):
        run('rm -rf /data/mdindex/yilu/tpch100')
    
    run('mkdir /data/mdindex/yilu/tpch100')
    
    if not exists('/data/mdindex/yilu/tpch100/lineitem'):
        run('mkdir /data/mdindex/yilu/tpch100/lineitem')
    if not exists('/data/mdindex/yilu/tpch100/customer'):
        run('mkdir /data/mdindex/yilu/tpch100/customer')
    if not exists('/data/mdindex/yilu/tpch100/part'):
        run('mkdir /data/mdindex/yilu/tpch100/part')
    if not exists('/data/mdindex/yilu/tpch100/orders'):
        run('mkdir /data/mdindex/yilu/tpch100/orders')
    if not exists('/data/mdindex/yilu/tpch100/supplier'):
        run('mkdir /data/mdindex/yilu/tpch100/supplier')
 
    
    global counter
    with cd('/data/mdindex/yilu'):
        script = "#!/bin/bash\n"
        script += "/home/mdindex/hadoop-2.6.0/bin/hadoop fs -get " + \
            "/user/yilu/tpch100-spark/lineitem/part-*%d /data/mdindex/yilu/tpch100/lineitem\n" % counter 
        script += "/home/mdindex/hadoop-2.6.0/bin/hadoop fs -get " + \
            "/user/yilu/tpch100-spark/customer/part-*%d /data/mdindex/yilu/tpch100/customer\n" % counter
        script += "/home/mdindex/hadoop-2.6.0/bin/hadoop fs -get " + \
            "/user/yilu/tpch100-spark/part/part-*%d /data/mdindex/yilu/tpch100/part\n" % counter 
        script += "/home/mdindex/hadoop-2.6.0/bin/hadoop fs -get " + \
            "/user/yilu/tpch100-spark/orders/part-*%d /data/mdindex/yilu/tpch100/orders\n" % counter 
        script += "/home/mdindex/hadoop-2.6.0/bin/hadoop fs -get " + \
            "/user/yilu/tpch100-spark/supplier/part-*%d /data/mdindex/yilu/tpch100/supplier\n" % counter 
        run('echo "%s" > download_data.sh' % script)
        run('chmod +x download_data.sh')

    counter += 1

@parallel
def download_data():
    run('nohup /data/mdindex/yilu/download_data.sh >> /tmp/xxx 2>&1 < /dev/null &', pty=False)


