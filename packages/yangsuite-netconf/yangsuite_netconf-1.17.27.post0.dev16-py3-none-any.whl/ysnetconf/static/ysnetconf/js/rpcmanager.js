/**
 * Module for handling RPC operations
 */
let rpcmanager = function() {
    "use strict";

    let config = {
        progressBar: "div#ys-progress",
        protoOpSelect: '#ys-proto-op',
        withDefaultsSelect: '#ys-with-defaults',
        editOpClass: '.ytool-edit-op',
        rpcConfigClass: '.ys-cfg-rpc',
        rpcInfoTextarea: 'textarea#ytool-rpc-info',
        rpcTextarea: 'textarea#ytool-rpc-data',
        deviceSelect: 'select#ys-devices-replay',
        deviceRunSelect: 'select#ys-open-device-window',
        datastoreGroup: '#ys-datastore-group',
        gentypeSelect: '#ys-rpctype',
        prefixSelect: '[name=ys-rpcprefixes]:checked',
        testDiv: 'div#ytool-test-col',
        ansibledialog:'div#ys-ansible',
        getURI: '/netconf/getrpc/',
        getAnsibleURI: '/netconf/getansible/',
        getTaskURI: '/netconf/gettaskrpc/',
        commitURI: '/netconf/getcommit/',
        runURI: '/netconf/runrpc/',
        runResultURI: '/netconf/runresult/',
        segmentctr: 1,
        savedrpcs: [],
        flags:{
            xpath_merge: true
        }
    };

    let locals = {
        keepAlives: {},
    };

    /**
     * This will be the new object created to send back config data
     * to construct a Netconf RPC
     *
     * @param {Object} node - A single jsTree node
     */
    function rpcCfg(node) {
        this.xpath = node.data.xpath_pfx.slice(0);
        if (node.value && !node.data.xpath_pfx.endsWith(']')) {
            this.value = node.value.slice(0);
        } else {
            // Path to a list so key value is in the xpath.
            this.value = '';
        }
        if (node.data.key) {
            this.key = true;
        }
        if (node.xml_value) {
            this.xml_value = node.xml_value.slice(0);
        }
        if (node.data.members) {
            this.members = [...node.data.members];
        }
        if (node.data.leafref_path) {
            this.leafref_path = node.data.leafref_path;
            if (this.leafref_path.startsWith("../")) {
                let path = node.data.leafref_path.split('/').slice(1);
                let base = node.data.xpath_pfx.slice(0);
                base = base.split('/');
                for (let seg of path) {
                    if (seg == '..') {
                        base.pop();
                        continue;
                    } else {
                        if (!seg.includes(':')) {
                            seg = node.data.prefix + ':' + seg;
                        }
                        base.push(seg);
                    }
                }
                this.leafref_path = base.join('/');
            }
        }
    };

    /*
     * Find the module node that owns this node.
     * node.parents = [parent_id, grandpt_id, ..., module_id, "#"]
     */
    function getModule(node, modules, tree) {
        let moduleid = node.parents[node.parents.length - 2];
        let moduleNode = tree.get_node(moduleid);

        let moduleName = moduleNode.data.module;
        /* Initialize the config data for this module if needed. */
        if (!modules[moduleName]) {
            modules[moduleName] = {
                revision: moduleNode.data.revision,
                namespace_prefixes: moduleNode.data.namespace_prefixes,
                configs: {}
            };
        }
        return [modules, moduleName];
    }

    /**
     * Configured values were scraped from the HTML elements and
     * put in objects.  Here we pre-process the values and convert
     * them to JSON
     *
     * @param {Object} tree - Top of jsTree
     * @returns {object} rpcs - All data used to construct a collection of RPCs
     *
     * rpcs = {
     *   'proto-op': 'edit-config',
     *   'dsstore': 'running',
     *   'with-defaults': '',
     *   'modules': {
     *     'modA': {
     *       'revision': "2015-01-01",
     *       'namespace_prefixes': { ... },
     *       'configs': [ {...}, {...}, ],
     *     },
     *     'modB': {...}
     *   }
     * }
     */
    function getRPCconfigs(tree, flags={}) {
        if (!tree.jstree(true)) {
            return;
        }
        let modules = {};
        let moduleName = "";
        let rpcs = {};
        let movedRows = {};
        let listsKeys = new Set();
        let notReferredTo = [];
        let nodeStack = rpc_ui.getNodesWithValues(tree);

        // Get operation nodes
        let opStack = rpc_ui.getNodesWithOperations(tree);

        // Check if there are no values but there are operation nodes
        if (nodeStack.length === 0) {
            // If there are no operations either, show alert and return
            if (opStack.length === 0) {
                alert('Values must be set in tree to "Build RPC"');
                return;
            }

            // Check if any operation nodes are containers with delete operation
            let hasDeleteContainers = opStack.some(node =>
                node.data.nodetype === 'container' &&
                (node['edit-op'] === 'delete' || node['edit-op'] === 'remove')
            );

            if (!hasDeleteContainers) {
                alert('Values must be set in tree to "Build RPC"');
                return;
            }

            // Otherwise continue - we have container delete operations
        } else {
            // Need to fixup nodes xpaths if keys are involved.
            rpc_ui.updateListKeyXPaths(nodeStack);
        }

        rpcs['proto-op'] = ($(config.protoOpSelect).val() ||
                            $(config.protoOpSelect).attr('data-value'));
        rpcs['dsstore'] = ($(config.targetSelect).val() ||
                           $(config.datastoreGroup).find(".selected").attr('data-value'));
        rpcs['with-defaults'] = $(config.withDefaultsSelect).val();

        /*
         * Iterate over every user selection in the Value column and create
         * appropriate configuration for backend to build RPC.
         */
        for (let node of nodeStack) {
            let modules_name = getModule(node, modules, tree.jstree(true));

            modules = modules_name[0];
            moduleName = modules_name[1];

            /* What row number of the visible jstree-grid are we in? */
            let row = $(node.element)
                .closest(".jstree-grid-column")
                .children("div")
                .index(node.element.parentElement);

            /* Update existing entry for this row, or create a new one */
            let cfg = (modules[moduleName].configs[row] ||
                        modules[moduleName].configs[movedRows[row]] ||
                        new rpcCfg(node, tree));
            cfg['nodetype'] = node.data.nodetype || '';
            cfg['datatype'] = node.data.basetype || node.data.datatype || '';
            cfg['default'] = node.data.default || '';

            if (cfg.leafref_path) {
                notReferredTo.push(cfg);
            }

            /*
             * For an edit-config (but not a get or get-config), it's
             * probably not a valid RPC if we have list contents but
             * haven't specified the list keys. Check for that.
             */
            if (rpcs['proto-op'] == 'edit-config') {
                let grandparentXPath = "";
                /* Walk from the root of the tree down to the node itself */
                for (let parentid of Array.from(node.parents).reverse()) {
                    if (parentid == "#") { continue; }
                    let parentNode = tree.jstree(true).get_node(parentid);
                    if (parentNode.data.nodetype == 'list') {
                        // TODO: does not catch sublists with duplicate key names.
                        if (parentNode.data.keys.length > 0) {
                            parentNode.data.keys.forEach(function(k) {
                                if (cfg.xpath.indexOf(k+'=') == -1) {
                                    listsKeys.add(k);
                                }
                            });
                        }
                    }
                    grandparentXPath = parentNode.data.xpath_pfx;
                }
            }
            let isSubPath = false;
            // if xpath_merge, then merge xpaths else no
            if(flags.xpath_merge){
                for (let rowCfg of Object.entries(modules[moduleName].configs)) {
                    /* List nodes may already be represented in another path so
                    * don't add them, example:
                    * /my/list/node[key=value]
                    * /my/list/node[key=value]/already/in/leaf/node/xpath
                    */
                    if (cfg.xpath.includes(rowCfg[1].xpath)) {
                        const cfgXpath = cfg.xpath.split("/");
                        const cfgLeafName = cfgXpath[cfgXpath.length - 1];
                        const rowCfgXpath = rowCfg[1].xpath.split("/");
                        const rowCfgLeafName = rowCfgXpath[rowCfgXpath.length -1];
                        if (!cfgLeafName.includes(rowCfgLeafName) || cfgLeafName == rowCfgLeafName) {
                            if (cfg.xpath == rowCfg[1].xpath) {
                                // Check if the nodetype is leaf-list, so
                                // that it can have multiple entries.
                                if (cfg['nodetype'] == 'leaf-list' && rowCfg[1].nodetype == 'leaf-list') {
                                    if (cfg.value != rowCfg[1].value) {
                                        continue;
                                    }
                                }
                            }
                            if (!modules[moduleName].configs[rowCfg[0]].key){
                                modules[moduleName].configs[rowCfg[0]] = cfg;
                                movedRows[row] = rowCfg[0];
                                isSubPath = true;
                            }
                            break;
                        }
                    }
                }
            }
            if (!isSubPath) {
                modules[moduleName].configs[row] = cfg;
            }
        }
        for (let ref of notReferredTo) {
            for (let rowCfg of Object.entries(modules[moduleName].configs)) {
                if (rowCfg[1].xpath == ref.leafref_path) {
                    rowCfg[1].referred_to = ref;
                }
            }
        }
        // Update opStack if it already exists
        opStack = rpc_ui.getNodesWithOperations(tree);
        if (opStack.length > 0) {
            // Need to fixup nodes xpaths if keys are involved.
            rpc_ui.updateListKeyXPaths(nodeStack.concat(opStack));
        }
        /*
         * Iterate over every user selection in the Operation column and add
         * edit-ops to the configuration for backend build of RPC.
         */
        for (let node of opStack) {
            let modules_name = getModule(node, modules, tree.jstree(true));
            let node_added = false

            modules = modules_name[0];
            moduleName = modules_name[1];

            /* What row number of the visible jstree-grid are we in? */
            let row = $(node.element)
                .closest(".jstree-grid-column")
                .children("div")
                .index(node.element.parentElement);

            if ($.isEmptyObject(modules[moduleName].configs)) {
                let cfg = new rpcCfg(node);
                cfg['nodetype'] = node.data.nodetype;
                cfg['edit-op'] = node['edit-op'];
                modules[moduleName].configs[row] = cfg;
                node_added = true
            } else if (node.data.nodetype == "list") {
                let chld = $(tree).jstree(true).get_node(node.children[0]);
                let cfg = new rpcCfg(chld);
                cfg['nodetype'] = node.data.nodetype;
                cfg['edit-op'] = node['edit-op'];
                let listRow = null;
                for (let rowCfg of Object.entries(modules[moduleName].configs)) {
                    // check if list is represented in other configs.
                    if (rowCfg[1].xpath == cfg.xpath) {
                        rowCfg[1]['edit-op'] = cfg['edit-op'];
                        break;
                    }
                    if (rowCfg[1].xpath.includes(cfg.xpath)) {
                        // found it in this xpath
                        listRow = rowCfg[0];
                        break;
                    }
                }
                if (listRow) {
                    if (Object.keys(modules[moduleName].configs).includes(String(Number(listRow)-1))) {
                        // This position is already taken so might have to move it.
                        for (let i=String(Number(listRow)-2); i>0; i--) {
                            if (!Object.keys(modules[moduleName].configs).includes(i)) {
                                modules[moduleName].configs[i] = modules[moduleName].configs[Number(listRow)-1];
                                modules[moduleName].configs[Number(listRow)-1] = cfg;
                                break;
                            }
                        }
                    } else {
                        modules[moduleName].configs[Number(listRow)-1] = cfg;
                    }
                }
                node_added = true;
            } else if (node.data.nodetype == "container") {
                // edit-op on container so add config to correct location
                let cfg = new rpcCfg(node);
                cfg['nodetype'] = node.data.nodetype;
                cfg['edit-op'] = node['edit-op'];
                if (node.data.presence) {
                    modules[moduleName].configs[row] = cfg;
                    node_added = true;
                }
                let delCfgs = [];
                for (let rowCfg of Object.entries(modules[moduleName].configs)) {
                    if (rowCfg[1].xpath.includes(cfg.xpath) && row < rowCfg[0]) {
                        modules[moduleName].configs[row] = cfg
                        node_added = true;
                    }
                    if (["delete", "remove"].indexOf(node['edit-op']) > -1) {
                        // All configs below deleted container are not needed
                        if (rowCfg[1].xpath.includes(cfg.xpath) && row < rowCfg[0]) {
                            delCfgs.push(rowCfg[0]);
                        }
                    }
                }
                // remove any configs not needed for delete/remove
                for (let dcfg of delCfgs) {
                    delete modules[moduleName].configs[dcfg];
                }
            } else {
                // edit-op config is already in configs
                for (let rowCfg of Object.entries(modules[moduleName].configs)) {
                    if (row in movedRows) {
                        row = movedRows[row];
                    }
                    if (row == rowCfg[0]) {
                        modules[moduleName].configs[row]['edit-op'] = node['edit-op'];
                        node_added = true
                        break;
                    }
                }
            }
            // edit-op without a value in value column
            if ((!Object.keys((modules[moduleName].configs)).includes(String(row))) && (node_added==false)){
                let cfg = new rpcCfg(node);
                cfg['edit-op'] = node['edit-op'];
                cfg['nodetype'] = node.data.nodetype;
                modules[moduleName].configs[row] = cfg;
            }
        }
        if (listsKeys.size > 0) {
            let warningDialog = $("<div>").text(
                "The following list(s) are missing values for one or more of " +
                    "their list keys. The resulting RPC may not be valid " +
                    "unless the keys are specified.");
            let warningList = $("<ul>");
            for (let lmk of listsKeys) {
                warningList.append($("<li>").text(lmk));
            }
            warningDialog.append(warningList);
            warningDialog.dialog({
                height: "auto",
                maxHeight: $(window).height() * 0.9,
                width: "auto",
                maxWidth: $(window).width() * 0.9,
                title: "Missing list keys",
            }).dialog("open");
        }

        /*
         * Now we must make each module.configs into an Array of rpcCfg
         */
        for (let moduleName in modules) {
            if (!modules.hasOwnProperty(moduleName)) {
                continue;
            }
            let module = modules[moduleName];
            module.configs = Object.values(module.configs);
        }
        rpcs['modules'] = modules;

        // clean up the nodes.
        for (let n of nodeStack) {
            delete n.value;
            delete n.xml_value;
        }
        for (let n of opStack) {
            delete n['edit-op'];
        }

        return rpcs;
    };

    /**
     * Asynchronous function that resends node data to backend to change
     * the format of the display.
     *
     * @param {string} gentype - basic or raw format.
     * @param {string} prefix_namespaces - 'minimal' or 'always'
     */
    function reloadRPCs(gentype, prefix_namespaces) {
        if (config.savedrpcs.length < 1) {
            return;
        }
        if (gentype == "script") {
            /* Club all RPCs together into a single API call */
            let data = {"gentype" : "script",
                        "prefix_namespaces": prefix_namespaces};
            data['cfgd'] = config.savedrpcs;
            let lastrpc = config.savedrpcs[config.savedrpcs.length - 1];
            $.when(jsonPromise(config.getURI, data)).then(function(retObj) {
                let infostrings = [];
                $.each(config.savedrpcs, function(i, data) {
                    $.each(data.cfgd.modules, function(key, value) {
                        infostrings.push(key + ": " + value.revision);
                    });
                });
                updateRPCText(retObj.reply, infostrings);

                $(config.testDiv).remove();
            }, function(retObj) {
                popDialog("Error " + retObj.status + ": " + retObj.statusText);
            });
            return;
        }

        /* For all other gentypes, we request one RPC at a time. */
        $.each(config.savedrpcs, function(i, data) {
            data['gentype'] = gentype;
            data["prefix_namespaces"] = prefix_namespaces;
            $.when(jsonPromise(config.getURI, data)).then(function(retObj) {
                let infostrings = [];
                $.each(data['cfgd'].modules, function(key, value) {
                    infostrings.push(key + ": " + value['revision']);
                });
                updateRPCText(retObj.reply, infostrings);

                $(config.testDiv).remove();
            }, function(retObj) {
                popDialog("Error " + retObj.status + ": " + retObj.statusText);
            });
        });
    }

    /**
     * Download the RPCs as a standalone Python script
     */
    function downloadScript() {
        let rpc_data = config.savedrpcs
        let string_rpc = false
        if ($("#ytool-rpc-data").hasClass("source-of-truth") &&
          $("#ytool-rpc-data").val()) {
            string_rpc = true
            rpc_data = $("#ytool-rpc-data").val()
        }
        if (rpc_data == ""){
          popDialog(" RPC Not Found")
          return;
        }
        let data = {
            gentype: 'script',
            prefix_namespaces: $(config.prefixSelect).val(),
            cfgd: rpc_data,
            string_rpc : string_rpc,
        };
        $.when(jsonPromise(config.getURI, data)).then(function(retObj) {
            let element = document.createElement("a");
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' +
                                 encodeURIComponent(retObj.reply));
            element.setAttribute('download', 'script.py');
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }, function(retObj) {
            popDialog("Error " + retObj.status + ": " + retObj.statusText);
        });
    };



    /**
     * Open the dialog box for "Ansible Playbook settings" values.
     *
     */
    function getAnsibleDialog() {
        fillAnsibleDialog();
        $(config.ansibledialog)
            .dialog({
                title: "Ansible Playbook Settings",
                minHeight: 222,
                minWidth: 760,
                buttons: {
                    "Download Playbook": function () {
                      let f_name = "ansible.yaml"
                      let p_name = "NETCONF playbook"
                      let t_name = "NETCONF RPC"
                      if($("#ys-ansible-file-name").val() != ""){
                          f_name = $("#ys-ansible-file-name").val()
                      }
                      if($("#ys-ansible-play-name").val() != ""){
                          p_name = $("#ys-ansible-play-name").val()
                      }
                      if($("#ys-ansible-task-name").val() != ""){
                          t_name = $("#ys-ansible-task-name").val()
                      }
                      downloadAnsible(f_name, p_name, t_name)
                      $(this).dialog("close")
                    },
                    "Cancel": function () {
                        $(this).dialog("close")
                    }
                }
            });
    }
    /**
     * Helper function to getAnsibleDialog() and getSaveDialog().
     */
    function fillAnsibleDialog(task) {
        let dialogHtml = $("<div>");
        dialogHtml
            .append($('<div class="form-group label--inline">')
                    .append($('<div class="form-group__text">')
                            .append('<label for="ys-ansible-name">Ansible file name</label>')
                              .append('<input type=text id="ys-ansible-file-name" placeholder="ansible.yaml"/>')))
            .append($('<div class="form-group label--inline">')
                    .append($('<div class="form-group__text">')
                            .append('<label for="ys-ansible-name">Ansible playbook name</label>')
                              .append('<input type=text id="ys-ansible-play-name" placeholder="NETCONF playbook" />')))
            .append($('<div class="form-group label--inline">')
                    .append($('<div class="form-group__text">')
                            .append('<label for="ys-ansible-name">Ansible  task name</label>')
                              .append('<input type=text id="ys-ansible-task-name" placeholder="NETCONF RPC"/>')))

        $(config.ansibledialog).empty().html(dialogHtml);
    }

    /**
     * Download the RPCs as a standalone Python script
     */
    function downloadAnsible(f_name,p_name,t_name) {
        let string_rpc = false
        let rpc_data = config.savedrpcs
        if ($("#ytool-rpc-data").hasClass("source-of-truth") &&
          $("#ytool-rpc-data").val()) {
            string_rpc = true
            rpc_data = $("#ytool-rpc-data").val()
        }
        if (rpc_data == ""){
          popDialog(" RPC Not Found")
          return;
        }
        let file_ext = f_name.split('.').pop()
        let file_name = f_name
        if ((file_ext == 'yaml') || (file_ext == 'yml')){
            file_name = f_name
        }
        else if (f_name.includes('.')){
            file_name = f_name.substr(0, f_name.lastIndexOf(".")) + '.yaml'
        }
        else {
            file_name = f_name + '.yaml'
        }
        let data = {
            proto_op: $(config.protoOpSelect).val(),
            prefix_namespaces: $(config.prefixSelect).val(),
            cfgd: rpc_data,
            string_rpc : string_rpc,
            p_name : p_name,
            t_name : t_name
        };
        $.when(jsonPromise(config.getAnsibleURI, data)).then(function(retObj, status_code) {
            let element = document.createElement("a");
            if (status_code == 'success') {
              element.setAttribute('href', 'data:text/x-yaml;charset=utf-8,' +
                                   encodeURIComponent(retObj.reply));
              element.setAttribute('download', file_name);
            }
            else{
                popDialog("Error Occured : " + retObj.reply);
            }
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }, function(retObj) {
            popDialog(" Some Error Occured, Please check the RPC Data ");
        });
    };


    /**
     * Asynchronous function that sends node data to backend to be converted
     * to XML format that complies with Netconf.
     *
     * @param {Object} tree - Top of jsTree.
     * @param {string} gentype - Format of display (basic, raw).
     * @param {string} addcommit - Specify whether to add a commit action.
     * @param {string} prefix_namespaces - Preferred handling for XML
     *                    namespace prefixes. Options: 'always', 'minimal'
     */
    function addRPC(tree, gentype, addcommit="", prefix_namespaces='always') {
        let data = {};
        let rpccfg = getRPCconfigs(tree, config.flags);

        if ($.isEmptyObject(rpccfg.modules)) {
            if (rpccfg['proto-op'] == 'edit-config') {
                popDialog('To construct an "edit-config" RPC, you must ' +
                          'select at least one item in the Value and/or ' +
                          'Operation columns.');
                return;
            } else if (rpccfg['proto-op'] == 'rpc' || rpccfg['proto-op'] == 'custom') {
                popDialog('To construct any given RPC, you must select ' +
                          'at least one item in the Value column.');
                return;
            } else {
                popDialog('Constructing an empty "' + rpccfg['proto-op'] + '"' +
                          ' RPC. If this is not what you intended to do, ' +
                          ' be sure to select at least one item in the Value column.');
                // continue;
            }
        }
        data['gentype'] = gentype;
        data['commit'] = addcommit;
        data['prefix_namespaces'] = prefix_namespaces;
        data['segment'] = config.segmentctr++;
        data['cfgd'] = rpccfg;

        config.savedrpcs.push(data);

        if (gentype == "script") {
            data = {'gentype': 'script', 'cfgd': config.savedrpcs};
            // We re-generate the entire script, so clear existing script:
            $(config.rpcTextarea).val('');
        }

        $.when(jsonPromise(config.getURI, data)).then(function(retObj) {
            let infostrings = [];
            $.each(rpccfg.modules, function(key, value) {
                infostrings.push(key + ": " + value['revision']);
            });
            updateRPCText(retObj.reply, infostrings);

            $(config.testDiv).remove();
        }, function(retObj) {
            popDialog("Error " + retObj.status + ": " + retObj.statusText);
        });
    };

    /**
     * Clear data and counters for fresh start
     */
    function clearRPC() {
        config.segmentctr = 1;
        // Remove pointer to saved RPCs, then reinitialize it.
        delete config.savedrpcs;
        config.savedrpcs = [];
    }

    /**
     * Helper function for addRPC() and addCommit()
     *
     * @param {string} rpc string to populate XML in textarea.
     * @param {Array} infostrings - array of module information strings to
     *                              populate textarea.
     */
    function updateRPCText(rpc, infostrings) {
        for (let info of infostrings) {
            let oldinfo = $(config.rpcInfoTextarea).val();
            if (oldinfo && oldinfo.length == 0) {
                $(config.rpcInfoTextarea).val(info);
            } else if (oldinfo && oldinfo.length > 0 && oldinfo.indexOf(info) < 0) {
                $(config.rpcInfoTextarea).val(oldinfo + "\n" + info);
            }
        }
        let oldrpc = $(config.rpcTextarea).val();
        if (oldrpc) {
            oldrpc += "\n";
        }
        $(config.rpcTextarea).val(oldrpc + rpc);
    };

    /**
     * Helper function to clear info and rpc textarea
     */
    function clearRPCText() {
        $(config.rpcInfoTextarea).val("");
        $(config.rpcTextarea).val("");
    }

    /**
     * Polling mechanism between master window and result windows.
     *
     * @param {string} device - name of device assigned to window
     * @param {number} retry - if polling fails try it again
     */
    function checkKeepAlive(device, retry=1) {
        if (Object.keys(locals.keepAlives).length == 0) {
            console.log("keepAlives references are gone!");
            return;
        }
        let keepAlive = locals.keepAlives[device];
        if (!keepAlive) {
            console.log("keepAlive for " + device + " missing")
            return;
        }
        if (keepAlive.win.runStatus == "unknown") {
            /* window state not changed to alive */
            if (retry) {
                keepAlive.win.runStatus == "alive"
                /* try one more time just in case we are out of sync */
                console.log("Retry keep alive - run window unknown state");
                checkKeepAlive(device, retry=0);
                return;
            }
            /* window has stopped pinging so stop checking */
            console.log("Run window not responding. Terminating session");
            clearInterval(keepAlive.clearID);
            delete locals.keepAlives[device];
            netconf.startEndSession(device, 'end');
            $(config.deviceRunSelect).val("none");
        } else if (keepAlive.win.runStatus == "alive") {
            /* window set alive state so reset it and wait for next check */
            keepAlive.win.runStatus = "unknown";
        } else {
            /* window state not determined */
            if (retry) {
                /* try one more time just in case we are out of sync */
                console.log("Retry keep alive - run window invalid state.");
                checkKeepAlive(device, retry=0);
                return;
            }
            console.log("Run window has invalid state. Terminating session");
            clearInterval(keepAlive.clearID);
            delete locals.keepAlives[device];
            netconf.startEndSession(device, 'end');
            $(config.deviceRunSelect).val("none");
        }
    }

    /**
     * Start a window that sets status to "alive" every "interval" seconds.
     * The parent that spawns the window can then check that status to make
     * sure the window is still alive.
     *
     * @param {object} index - Index to map that contains a window reference
     * @param {integer} interval - Seconds between status check
     */
    function openDeviceWindow(index, interval=1500, windowOrTab="tab") {
        if (!locals.keepAlives[index]) {
            let win = null;
            /* open a result window that sets status periodically */
            if (windowOrTab === "tab") {
                win = window.open(
                    config.runResultURI + index,
                    "_blank");
            } else if (windowOrTab === "pop") {
                win = window.open(
                    config.runResultURI + index,
                    'YANG Suite Run ' + index,
                    "height=2560px overflow=auto width=1271px, scrollbars=yes");
            } else {
                return;
            }
            if (!win) {
                alert("Window failed to open...popups blocked?");
                return;
            } else {
                win.runStatus = "alive";
                win.focus();
            }

            /* check every "interval" seconds to see if the window is still alive */
            let clearID = setInterval(function() {
                checkKeepAlive(index);
            }, interval);
            locals.keepAlives[index] = {win: win, clearID: clearID};
        }
    }

    /**
     * Asynchronous function that sends node data to backend to send to device.
     *
     * @param {string} device - Slug identifying device profile to send to
     * @param {string} datastore - Datastore RPC applies to, if any
     * @param {array, string} rpcs - Array of Objects that contains the node
     *     data, OR (if custom) an XML string.
     * @param {boolean} custom - Flag specifying a custom RPC to be sent instead
     *                           of node data.
     */
    function runRPC(device, rpcs, custom=false) {
        let data = {};

        if (!device) {
            popDialog("Please Select Device");
            return;
        }
        $(config.testDiv).remove();

        data = {
            device: device,
        };
        if (custom) {
            data['custom'] = "true";
            data['rpcs'] = rpcs;
        } else {
            data['rpcs'] = rpcs;
        }

        $.when(jsonPromise(config.runURI, data)).then(function(retObj) {
            if (!retObj) {
                // TODO is clearInterval appropriate here?
                clearInterval(locals.keepAlives[device]);
                delete locals.keepAlives[device];
                return;
            }
            if (retObj.error) {
                // TODO is clearInterval appropriate here?
                clearInterval(locals.keepAlives[device]);
                delete locals.keepAlives[device];
                return;
            }
            config.segmentctr = 1;
        }, function(retObj) {
            popDialog('Error' + retObj.status + ':' + retObj.statusText);
        });

    };

    /**
     * Send a canned 'commit' RPC to the given device.
     */
    function sendCommitRPC(device) {
        runRPC(device,
`<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <commit/>
</rpc>`, true);
    };

    /**
     * Send a canned unfiltered 'get-config' RPC for the given datastore
     */
    function sendGetConfigAllRPC(device, dsstore) {
        runRPC(device,
`<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <get-config>
    <source>
      <${dsstore}/>
    </source>
  </get-config>
</rpc>`, true);
    };

    /**
     * Send a canned RFC 5277 'get streams' RPC to the given device
     */
    function sendGetStreamsRPC(device) {
        runRPC(device,
`<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <get>
    <filter type="subtree">
      <netconf xmlns="urn:ietf:params:xml:ns:netmod:notification">
        <streams/>
      </netconf>
    </filter>
  </get>
</rpc>`, true);
    }

    /**
     * Send a canned RFC 5277 'create-subscription' RPC for the given stream.
     */
    function sendSubscribeRPC(device, eventstream) {
        runRPC(device,
`<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <create-subscription xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <stream>${eventstream}</stream>
  </create-subscription>
</rpc>`, true);
    }

    /**
     * Load a replay task and create NETCONF RPCs based on the metadata
     *
     * @param {string} name - Name of replay task to load.
     */
    function loadTask(name, gentype="basic", category="default", variables={}) {

        let data = {'name': name,
                    'gentype': gentype,
                    'prefixes': $(config.prefixSelect).val(),
                    'dsstore': ($(config.targetSelect).val() ||
                                $(config.datastoreGroup).find(".selected").attr('data-value')),
                    'category': category,
                    'variables': JSON.stringify(variables)};

        let progressBar = startProgress($(config.progressBar), "", "",
                                        "Loading replay XML...");

        $.when(getPromise(config.getTaskURI, data))
        .then(function(retObj) {
            if (!retObj) {
                // TODO: fail/suscces not returned
                popDialog("GET Task " + name + " failed");
                return;
            }
            if (retObj.error) {
                popDialog(retObj.error);
                return;
            }

            clearRPCText();

            let text = "";
            for (let txt of retObj.info) {
                text += txt[0] + ": " + txt[1];
            }
            $(config.rpcInfoTextarea).val(text)

            updateRPCText(formatXml(retObj.segments), text);

            $(config.testDiv).remove();
            stopProgress(progressBar);
        })
        .fail(function(retObj) {
            stopProgress(progressBar);
            let t = retObj.responseText;
            popDialog(retObj.statusText + "<pre>" + t.slice(0, t.indexOf("\n\n")) + "</pre>");
        });
    };

    /**
     * Given replay contents as retrieved from tasks.getTask, populate
     * config.savedrpcs accordingly.
     */
    function populateSavedRPCsFromReplay(segments) {
        clearRPC();

        let anyCustom = false;
        for (let segment of segments) {
            if (segment.yang['proto-op'] == 'rpc') {
                anyCustom = true;
                continue;
            }
            let segdata = {
                cfgd: {
                    dsstore: $(config.datastoreGroup).find(".selected").attr('data-value'),
                    modules: segment.yang.modules,
                    "proto-op": segment.yang['proto-op'],
                },
                commit: segment.commit,
                gentype: $(config.gentypeSelect).val(),
                prefix_namespaces: $(config.prefixSelect).val(),
                segment: segment.segment,
            };

            config.savedrpcs.push(segdata);
        }

        if (anyCustom) {
            $(config.rpcTextarea).trigger('change');
        }
    };

    /**
     * Replay a saved task in NETCONF protocol.
     *
     * @param {string} name - Name of task to run.
     * @param {string} category - Category of task
     */
    function runTask(name, category, variables={}) {
        let data = {'task': name,
                    'category': category,
                    'prefixes': $(config.prefixSelect).val(),
                    'device': $(config.deviceSelect).val(),
                    'dsstore': ($(config.targetSelect).val() ||
                                $(config.datastoreGroup).find(".selected").attr('data-value')),
                    'variables': JSON.stringify(variables),
                   };

        $.when(jsonPromise(config.runURI, data)).then(function(retObj) {
            if (!retObj) {
                $(config.runDiv).append("<pre>RUN Task " + name + " failed</pre>");
                clearInterval(locals.keepAlives[data.device]);
                delete locals.keepAlives[data.device];
                return;
            }
            if (retObj.error) {
                $(config.runDiv).append("<pre>" + retObj.error + "</pre>");
                clearInterval(locals.keepAlives[data.device]);
                delete locals.keepAlives[data.device];
                return;
            }
        });

        openDeviceWindow(data.device, 1500);
    }

    /**
     * Public APIs
     */
    return {
        config: config,
        addrpc: addRPC,
        clearrpcs: clearRPC,
        runrpc: runRPC,
        sendCommitRPC: sendCommitRPC,
        sendGetConfigAllRPC: sendGetConfigAllRPC,
        sendGetStreamsRPC: sendGetStreamsRPC,
        sendSubscribeRPC: sendSubscribeRPC,
        reloadrpcs: reloadRPCs,
        downloadScript: downloadScript,
        downloadAnsible: downloadAnsible,
        getAnsibleDialog:getAnsibleDialog,
        getRPCconfigs: getRPCconfigs,
        updateRPCText: updateRPCText,
        loadtask: loadTask,
        populateSavedRPCsFromReplay: populateSavedRPCsFromReplay,
        runtask: runTask,
        openDeviceWindow: openDeviceWindow,
    };

}();
