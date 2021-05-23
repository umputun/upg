# Make command to use for dependencies
MAKECMD=make
                                                                                                                                                                                                                
# If no release is specified, 1 will be used                                                                                                        
ifndef RELEASE
RELEASE=1
endif

ifndef TAG
SVN_URL=http://upg.umputun.com/repos/trunk
endif

ifdef TAG
SVN_URL=http://upg.umputun.com/repos/tags/$(TAG)
endif

ifdef BRANCH
SVN_URL=http://upg.umputun.com/repos/branches/$(BRANCH)
endif

# if no VERSION is specified content of VERSION file will be used
ifndef VERSION
VERSION=`cat ./VERSION`
endif
                                                                                                        
DATE=`date +%Y%m%d`


.PHONY : update gz clean spec rpm html-doc pdf move-docs site index download upload remote


#build all (docs, gz, rpm and update site)
all: update spec gz rpm clean
	@echo "all done. $(VERSION)-$(RELEASE) was built"

update:
	@echo "Loading fresh copy of UPG ..."
	rm -r -f upg.dist
	mkdir -p upg.dist/tmp
	svn export $(SVN_URL) upg.dist/tmp --force

gz:
	cd upg.dist/tmp && python setup.py sdist
	mv upg.dist/tmp/dist/*.gz upg.dist
	
clean:
	rm -r -f upg.dist/tmp
	

#make spec file for DIST
spec:
	@echo $(VERSION)-$(RELEASE)
	cd upg.dist/tmp && python setup.py bdist_rpm --spec-only --release=$(RELEASE)
	cat upg.dist/tmp/dist/UPG.spec
	mv upg.dist/tmp/dist/UPG.spec upg.dist

#build rpm and srpm and copy to current dir
rpm:
	cd upg.dist/tmp && python setup.py bdist_rpm --release=$(RELEASE)
	mv upg.dist/tmp/dist/*.rpm upg.dist

	

#build rpm and gz only
prog:  update spec gz rpm

src:   update gz
	



