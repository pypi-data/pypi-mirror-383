/**
 * Module for handling the NETCONF controls
 */
let netconf = function() {

    let config = {
        /* store public configurations here */
        moduleSelect: '#ytool-models',
        yangsetSelect: '#ytool-yangset',
        protoOpSelect: '#ys-proto-op',
        datastoreGroup: "#ys-datastore-group",
        datastoreGroupButtons: "#ys-datastore-group .btn",
        progressBar: "div#ys-progress",
        selectedDevice: "#ys-devices-rpc",
        selectedDsstore: "#ys-target",
        retryTimer: "#ys-retry-timer",
        lockButton: "#ys-btn-lock span",
        lockTogglePrefix: "#ys-toggle-lock-",
        startSession: "button#ys-session-toggle",
        sessionStatusElem: null,
        lockUnlockDialog: "div#ys-lockunlock-dialog",
        lockSetURI: "/netconf/lock/set/",
        sessionStartEndURI: "/netconf/session/start_end/",
        lockCheckURI: "/netconf/lock/check/",
        selectedDeviceChanged: false,
        deviceDatastoreCache: {},
        addListNodes: [],
        addTreeNodes: []
    };

    function getProtocolOperation() {
        return ($(config.protoOpSelect).val() ||
                $(config.protoOpSelect).attr('data-value'));
    }

    /**
     * Creates the netconf config mode pulldown menu in a tree cell.
     *
     * If a node is a key or is mandatory, you should not be able to
     * delete it directly, however, if the node is a container, the intent
     * is to delete all resources in its subtree which is ok.  A container
     * is flagged as mandatory if any of its children are mandatory.
     *
     * @param {Object} node representing a YANG leaf, container, etc...
     */
    function buildEditProtocolOperationMenu(node) {
        let data = node.data;
        let edit_ops = ["merge", "delete", "replace", "create", "remove"];
        let target = $('<select class="ytool-edit-op" nodeid="'+node.id+'">');

        $.each(edit_ops, function(i, op) {
            if ((op == 'delete' || op == 'remove') &&
                (node.data.key == 'true' ||
                    (node.data.mandatory == 'true' &&
                     node.data.nodetype != 'container'))) {
                return true;
            }
            target.append('<option>'+op+'</option>');
        });
        target.append('</select>');
        return target;
    }

    /**
     * Refresh "NETCONF operation" button bar based on the
     * NETCONF global operations allowed/supported for the loaded YANG module(s)
     */
    function refreshProtocolOperationInputs() {
        let target = $("#ys-proto-op");
        let selection = ($(config.protoOpSelect).val() ||
                         $(config.protoOpSelect).attr('data-value'));

        // Disable all options to start with
        target.find("option, .btn").prop("disabled", true);

        let tree = $("#tree").jstree(true);
        // Iterate over top-level (module) nodes
        $.each(tree.get_node('#').children, function(i, id) {
            let node = tree.get_node(id);
            $.each(node.data.operations, function(i, op) {
                let option = target.find("#netconf-op-" + op);
                option.prop("disabled", false);
            });
        });

        // If previous selection is no longer active, change it to the
        // first available option.
        if (target.find('#netconf-op-' + selection).hasClass("disabled")) {
            let first = target.find('.btn:not(.disabled):first, ' +
                                    'option:not(.disabled):first');
            selection = first.val() || first.attr('data-value');
        }
        $('#ys-proto-op').val(selection).change();
    }

    /**
     * Refresh 'Datastore' options based on the selected device and NETCONF operation.
     */
    function refreshDatastores() {
        let proto_op = ($(config.protoOpSelect).val() ||
                        $(config.protoOpSelect).attr('data-value'));

        let dsmenu = $(config.datastoreGroup);
        let selection = dsmenu.find(".btn.selected").attr('data-value');

        $(config.datastoreGroupButtons).removeClass("selected");
        $(config.datastoreGroupButtons).addClass("disabled");

        for (let dsstore of config.deviceDatastoreCache[proto_op]) {
            let btn = dsmenu.find(".datastore-" + dsstore);
            btn.removeClass("disabled");
        }
        // If previous selection is no longer active, change to the first
        // available option.
        if (dsmenu.find('.datastore-' + selection).hasClass("disabled")) {
           let first = dsmenu.find(".btn:not(.disabled):first");
           selection = first.attr("data-value");
        }
        dsmenu.find('.datastore-' + selection).click();
    }



    /**
     * Based on the selected proto-op, show all nodes in the jstree grid that
     * are capable of this operation, and disable or hide all others.
     *
     * As iterating over the entire tree may be time-consuming (e.g. with
     * large models like Cisco-IOS-XE-native), we only filter the visible nodes.
     */
    function filterNodes() {
        let proto_op = ($(config.protoOpSelect).val() ||
                        $(config.protoOpSelect).attr('data-value'));
        let tree = $("#tree").jstree(true);
        let hide_disabled_nodes = $('input[name="hide-nodes"]:checked').val();

        let visible_node_elems = $("#tree").find("li.jstree-node").toArray();

        for (let node_elem of visible_node_elems) {
            let node = tree.get_node(node_elem.id);
            filterNode(node, tree, proto_op, (hide_disabled_nodes == 'hide'));
        }
        tree.redraw();
    }

    /**
     * Based on the given proto-op, show, hide, or disable the given node.
     *
     * @param {Object} node: jstree node
     * @param {Object} tree: jstree instance
     * @param {string} proto_op: Protocol operation - edit-config, get, etc.
     * @param {boolean} hide_disabled_nodes
     */
    function filterNode(node, tree, proto_op, hide_disabled_nodes) {
        let enable = false;
        /*
         * 'choice' and 'case' nodes have no applicable operations,
         * but share the visibility of their parent/child nodes.
         * We can just show/enable them unconditionally, as if their
         * parents are hidden, they will remain hidden regardless.
         */
        if (node.data.nodetype == 'case' ||
            node.data.nodetype == 'choice') {
            enable = true;
        }
        for (let p in node.data.operations) {
            let op = node.data.operations[p];
            /*
             * 'input' and 'output' are subtrees of a rpc. They're not
             * considered separate module-level operations, so show them
             * if we're looking for an RPC.
             *
             * Similarly, when dealing with 'action', allow inputs and outputs,
             * and also enable list keys in the path to the action.
             */
            if (op == proto_op ||
                (proto_op == 'rpc' && (op == 'input' || op == 'output')) ||
                (proto_op == 'action' && (op == 'input' ||
                                          op == 'output' ||
                                          node.data.key))) {
                enable = true;
                break;
            }
        }

        if (node.data.deviation == 'not-supported') {
            enable = false;
        }

        if (enable) {
            tree.enable_node(node);
            tree.show_node(node, skip_redraw=true);
        } else {
            tree.disable_node(node);
            /*
             * To reduce user consternation, never hide root (module)
             * nodes, even if disabled
             */
            if (hide_disabled_nodes && node.parent != "#") {
                tree.hide_node(node, skip_redraw=true);
            } else {
                tree.show_node(node, skip_redraw=true);
            }
        }
    }

    function jsTree(pth, names, yangset) {
        return rpc_ui.makeJSTreeGrid(names, yangset).then(function() {
            $(yangtree.config.tree).bind('loaded_grid.jstree', filterNodes);
            $(yangtree.config.tree).bind('loaded_grid.jstree',
                                       refreshProtocolOperationInputs);
            $(yangtree.config.tree).bind('after_open.jstree', function(e, data) {
                let tree = data.instance;
                let node = data.node;
                let hide_disabled_nodes = $('input[name="hide-nodes"]:checked').val();
                let proto_op = ($(config.protoOpSelect).val() ||
                                $(config.protoOpSelect).attr('data-value'));
                // Enable/disable/show/hide the revealed nodes as appropriate
                $.each(tree.get_children_dom(node), function(i, node_elem) {
                    filterNode(tree.get_node(node_elem.id), tree,
                               proto_op, (hide_disabled_nodes == 'hide'));
                });
            });
        });
    }

    /**
     * Public APIs
     */

    /**
    * Function to Lock/Unlock the datastore
    */
    function lockUnlockDatastore(lock, device, dsstore) {
        let data = {
            lock: lock,
            device: device,
            dsstore: dsstore,
        };
        data['retry_timer'] = $(config.retryTimer).val() || '45';
        $.when(jsonPromise(config.lockSetURI, data))
            .then(function(retObj) {
                // Check the message as we don't have a status flag - yuck
                if (retObj.resp == 'Datastore Locked' ||
                    retObj.resp == 'Datastore unlocked successfully' ||
                    retObj.resp == 'Already Unlocked') {
                    toggleLockButton(dsstore, lock);
                } else {
                    popDialog('Error: ' + retObj.resp);
                }
            }, function(retObj) {
                popDialog('Error' + retObj.status + ':' + retObj.statusText);
            });
    };

    /**
     * UI helper for lockUnlockDatastore
     */
    function toggleLockButton(dsstore, lock) {
        let btn = $(config.lockTogglePrefix + dsstore);
        let lockElem = btn.find('.icon');
        if (lock) {
            lockElem.removeClass("icon-unlock");
            lockElem.addClass("icon-lock");
            btn.addClass("btn--negative");
        } else {
            lockElem.removeClass("icon-lock");
            lockElem.addClass("icon-unlock");
            btn.removeClass("btn--negative");
        }
    };

    /**
     * UI helper for startEndSession
     *
     * @param {boolean} state - Is a session in progress?
     */
    function toggleSessionButton(state) {
        if (state) {
            $(config.startSession).text("End Session");
            $(config.startSession).removeClass("btn--primary");
            $(config.startSession).addClass("btn--negative");
            if (config.sessionStatusElem) {
                $(config.sessionStatusElem).text(
                    $(config.sessionStatusElem).text().replace("(not connected)",
                                                               "(connected)")
                );
            }
        } else {
            $(config.startSession).text("Start Session");
            $(config.startSession).removeClass("btn--negative");
            $(config.startSession).addClass("btn--primary");
            /* No locks when no session is in progress */
            for (let ds of ['candidate', 'running', 'startup']) {
                toggleLockButton(ds, false);
            }
            if (config.sessionStatusElem) {
                $(config.sessionStatusElem).text(
                    $(config.sessionStatusElem).text().replace("(connected)",
                                                               "(not connected)")
                );
            }
        }
    };

    /**
     * Function to start or end a netconf session.
     *
     * @param {string} device - Slug identifying the device profile of interest
     * @param {string} action - one of 'start', 'end'
     */
    function startEndSession(device, action) {
        let data = {
            device: device,
            session: action
        };
        if (action == 'start') {
            $(config.startSession).text("Starting Session...");
        } else {
            $(config.startSession).text("Ending Session...");
        }
        return $.when(jsonPromise(config.sessionStartEndURI, data))
            .then(function(retObj) {
                if (retObj.reply) {
                    // successful outcome
                    toggleSessionButton(action == 'start');
                } else {
                    // something went wrong - reset button to prior state
                    toggleSessionButton(action != 'start');
                }
            }, function(retObj) {
                popDialog('Error' + retObj.status + ':' + retObj.statusText);
            });
    };

    /**
     * Function to retrieve a set of all supported datastores from a device.
     * @param {string} device - Slug identifying the device profile of interest
     */
    function getAllDatastores(device) {
        return $.ajax({
            url: '/netconf/datastores',
            type: 'GET',
            data: {
                device: device,
                list_all: true,
            },
            dataType: 'json',
            error: function(data) {
                popDialog("Error " + data.status + ": " + data.statusText);
                $(config.datastoreGroupButtons).removeClass("disabled");
            }
        });
    }
    /**
     * Function to retrieve a mapping of operations to datastores from a device.
     */
    function getDatastores() {
        let proto_op = ($(config.protoOpSelect).val() ||
                        $(config.protoOpSelect).attr('data-value'));
        let device = $('select.ys-devices').val();

        if (!proto_op || !device) {
            // Default to all possible datastores until the user selects something
            $(config.datastoreGroupButtons).removeClass("disabled");
            return;
        }
        if (!config.selectedDeviceChanged) {
            refreshDatastores();
            return;
        }

        let progressBarText = "Device loading...";
        let progressBarDiv = startProgress($(config.progressBar),"","",progressBarText) || $(config.progressBar);

        $.ajax({
            url: '/netconf/datastores',
            type: 'GET',
            data: {
                device: device
            },
            dataType: 'json',
            success: function(data) {
                config.deviceDatastoreCache = data;
                config.selectedDeviceChanged = false;
                refreshDatastores();
                stopProgress(progressBarDiv);
            },
            error: function(data) {
                popDialog("Error " + data.status + ": " + data.statusText);
                $(config.datastoreGroupButtons).removeClass("disabled");
                stopProgress(progressBarDiv);
            }
        });
    };

    /**
     * Function to retrieve the NETCONF capabilities reported by a device.
     */
    function getCapabilities(device) {
        return $.ajax({
            url: '/netconf/capabilities',
            type: 'GET',
            data: {
                device: device,
            },
            dataType: 'json',
        });
    }

    /**
     * Function to set logging levels for ncclient operations.
     */
    function setLoggingLevel() {
        let loglevel = 'informational';
        if ($("#ys-logging").is(":checked")) {
            loglevel = 'debug';
        }
        $.when(getPromise('/netconf/setlog/', {"loglevel": loglevel}))
            .then(function(retObj) {
                if (retObj.reply) {
                    popDialog("NETCONF logging set to "+ loglevel.toUpperCase() +" level");
                }
            }, function(retObj) {
                popDialog('Error' + retObj.status + ':' + retObj.statusText);
            });
    }

    /*
     * Given a single configuration from a replay and the node ID of
     * the configuration's location on the tree, setGridValue adds the
     * value to the tree.
     */
    function setGridValue(gridNodeId, cfg, tree) {
        let gridCell = $("div.jstree-grid-col-1[data-jstreegrid=" + gridNodeId + "]");
        tree.trigger("select_cell.jstree-grid", {
            node: $("li#" + gridNodeId),
            column: "Value",
            grid: gridCell,
        });
        if (cfg.value !== undefined) {
            let gridCell = $("div.jstree-grid-col-1[data-jstreegrid=" + gridNodeId + "]");
            // Trigger selection again so node is setup with proper element.
            // TODO: why are 2 triggers required?
            $(segmentTree).trigger("select_cell.jstree-grid", {
                node: $("li#" + gridNodeId),
                column: "Value",
                grid: gridCell,
            });
            // Now set the replay value
            gridCell.find(".ys-cfg-rpc").val(cfg.value).change();
        }
        if (cfg["edit-op"]) {
            let opCell = $("div.jstree-grid-col-2[data-jstreegrid=" + gridNodeId + "]");
            tree.trigger("select_cell.jstree-grid", {
                node: $("li#" + gridNodeId),
                column: "Operation",
                grid: opCell,
            });
            let node = tree.get_node(gridNodeId);
            // Build edit-op selection element and select correct edit-op.
            opCell.append(buildEditProtocolOperationMenu(node));
            opCell.find('select option:contains("' + cfg["edit-op"] +'")').prop("selected", true);
        }
    }

    /**
     * Given a JSON tree in flat form, move to node that represents last
     * segment of an xpath.
     *
     * @param {Object} tree - JSON tree.
     * @param {Array} xps - List of segemnts of an xpath.
     *
     * Example:
     * /one/two/three/four
     * [one, two, three, four]
     *
     * @returns {Object} JSON tree with top node being last segment of xpath
     */
    function seekNode(tree, xps) {
        let xpath_pre = '';

        for (let seg of xps) {
            if (!seg) {
                continue;
            }
            xpath_pre = xpath_pre + '/' + seg
            seg_updated = seg.slice(seg.indexOf(":")+1);
            for (let i=0; i < tree.length; i++) {
                if (((tree[i].text == seg_updated) || (tree[i].text == seg)) && (tree[i].data.nodetype!='case')) {
                   tree_xpath = rpc_ui.removePredicate(tree[i].data.xpath_pfx);
                    if((tree[i].data.key == 'true') && ((!tree_xpath.endsWith(tree[i].text) ||(tree[i].data.xpath_pfx).endsWith(']') ))){
                      pfx = ''
                      if (!(tree[i].text).includes(':')){
                        pfx = tree[i].data.prefix+":";
                      }
                      tree_xpath = tree_xpath+'/'+pfx+tree[i].text;
                    }
                    if(xpath_pre == tree_xpath) {
                        tree = tree.slice(i);
                        break;
                    }
                }
            }
        }
        return tree;
    }

    /**
     * Helper function to check of list node has already been processed.
     *
     * @param {String} xp - xpath with keys filtered out.
     * @param {Array} lists - list nodes already processed in tree.
     * @returns {Number} - index of found list.
     */
    function findList(xp, lists) {
        let found = -1;
        for (let i=0; i<lists.length; i++)  {
            l = lists[i];
            lxp = rpc_ui.removePredicate(l.data.xpath_pfx);

            if (lxp == xp) {
                found = i;
                break;
            }
        }
        return found;
    }

    /**
     * Helper function to extract the keys at the end of an xpath.
     *
     * @param {String} xpKeys - xpath
     * @returns {Array} - list of Objects with key/value pairs.
     */
    function findKeys(xpKeys) {
        // Find the keys and their values from xpath.
        let keys = [];
        for (let i=0; xpKeys.endsWith(']'); i++) {
            let xKey = xpKeys.slice(xpKeys.lastIndexOf('['));
            xpKeys = xpKeys.replace(xKey, '');
            let key = xKey.slice(1,xKey.indexOf('='));
            // remove prefix from the key name
            key = key.slice(key.indexOf(':')+1)
            let value = xKey.slice(xKey.indexOf('=')+1, xKey.indexOf(']'));
            value = value.replaceAll('\"', '');
            keys.push({key: key, value: value})
        }
        return keys.reverse();
    }

    /**
     * Helper function that sets key grid values for a list node.
     *
     * @param {Object} node - JSON tree with list node at first position.
     * @param {Array} keys - List of keys from findKeys.
     */
    function setKeyValues(node, keys) {
        // Set key values that were found in xpath from findKeys.
        for (let i=0; i < keys.length; i++) {
            kv = keys[i];
            if (node[0].data.keys.includes(kv.key)) {
                let keyNode = node[i+1];
                tree.select_node(keyNode.id);
                setGridValue(keyNode.id, {value: kv.value}, tree);
            }
        }
    }

    /**
     * Set grid value and operation column for list node and it's keys.
     *
     * Xpath example:
     * /1/2[3=X]/4/5[6=Y]
     *
     * /1/2/3/4/5 list needs key 6 set to Y
     *
     * @param {div element} tree - pointer to tree div.
     * @param {Object} treedata - tree JSON.
     * @param {Object} cfg - replay config with xpath containing a key.
     * @param {Array} lists - lists already processed.
     */
    function addListNode(tree, treedata, listCfg, lists) {
        let listIndex = -1;
        let xpKeys = listCfg.xpath.slice(0);
        let xp = rpc_ui.removePredicate(listCfg.xpath);
        let xps = xp.split("/");
        let node = seekNode(treedata, xps);

        if (node.length == 0 || !xps.join('/').endsWith(node[0].text)) {
            // Is this an additional list?
            listIndex = findList(xps.join('/'), lists);
            if (listIndex  > -1) {
                // Add list entry
                let addedNodeId = rpc_ui.addTreeListEntry(lists[listIndex].id, tree, false);
                let listdata = tree.get_json(addedNodeId, {flat:true, no_children:false});
                lists[listIndex] = listdata[0];
                return addListNode(tree, listdata, listCfg, lists);
            }
        }

        if (node.length == 0) {
            return node;
        }
        if (!node[0].data || node[0].data.nodetype != 'list') {
            alert("Wrong nodetype encountered. Are you using the correct model version?");
            return node;
        }

        if (listCfg['edit-op']) {
            tree.select_node(node[0].id);
            setGridValue(node[0].id, {'edit-op': listCfg['edit-op']}, tree);
        }

        // Find the keys and set their values in the tree.
        let keys = findKeys(xpKeys);
        setKeyValues(node, keys);

        listIndex = findList(xps.join('/'), lists);
        if (listIndex == -1) {
            lists.push(node[0]);
        } else {
            lists[listIndex] = node[0];
        }

        return node.slice(keys.length+1);
    }

    /**
     * Make sure any embedded lists in xpath are set in tree.
     *
     * Xpath example:
     * /1/2[3=X]/4/5[6=Y]/7
     *
     * /1/2 list needs key 3 set to X
     * /1/2/3/4/5 list needs key 6 set to Y
     *
     * @param {div element} tree - pointer to tree div.
     * @param {Object} treedata - tree JSON.
     * @param {Object} cfg - replay config with xpath containing a key.
     * @param {Array} lists - lists already processed.
     */
    function setEmbeddedLists(tree, treedata, cfg, lists) {
        let xpKeys = cfg.xpath.slice(0);
        let embeddedLists = [];
        xpKeys = xpKeys.slice(0, xpKeys.lastIndexOf(']/')+2);
        while (xpKeys.endsWith(']/')) {
            let xp = xpKeys.slice(0, xpKeys.lastIndexOf('/'))
            embeddedLists.push(xp);
            xpKeys = xp.slice(0, xp.lastIndexOf(']/')+2);
        }
        for (xp of embeddedLists.reverse()) {
            let xps = rpc_ui.removePredicate(xp);
            if (findList(xps, lists) == -1) {
                addListNode(tree, treedata, {xpath: xp}, lists);
            }
        }
    }

    /**
     * Set grid value and operation column for replay node.
     *
     * @param {div element} tree - pointer to tree div.
     * @param {Object} treedata - tree JSON.
     * @param {Object} cfg - Object representing a replay node.
     */
    function addCfgNode(tree, treedata, cfg) {
        let xp = rpc_ui.removePredicate(cfg.xpath);
        let xps = xp.split("/");
        let node = seekNode(treedata, xps, []);

        if (!xps.join('/').endsWith(node[0].text)) {
            // Can't find my node so rewind.
            nodedata = tree.get_json(1, {flat: true, no_children:false});
            return addCfgNode(tree, nodedata, cfg);
        }
        if (node) {
            tree.select_node(node[0].id);
            setGridValue(node[0].id, cfg, tree);
            return node.slice(1);
        }
        return treedata;
    }

    /**
     * Function setNodesInTree.
     *
     * Set value and operation column with data obtained from replay.
     *
     * Walk the current tree and process each node. In case of a new
     * list entry, add JSON obects to the tree.
     *
     * Assumption:
     * - replays will always come in sequetial order with lowest tree
     *   node ID first and highest tree node ID last.
     *
     * Example:
     * - node1
     * - node2
     * - node3 - set node grid value and operation column
     * - node4
     * - node5 - list, check for node grid operation column
     * - node6 - this is key for list so set grid value column
     * - addition of list entry so insert new entry
     * - nodej1_140 - list, check for node grid operation column
     * - nodej1_141 - this is key for list so set grid value column
     * - node7
     * - nodeX - can't find node I was looking for so rewind tree
     * - node1
     * - node2
     * - node...
     * - nodeX - set node grid value and operation column
     * - ...
     *
     * @param {div element} tree - pointer to tree div.
     * @param {Object} treedata - tree JSON.
     * @param {Array} replayCfgs - Objects representing each replay node.
     * @param {Object} listCfg - list entry from replay configs.
     * @param {Array} lists - lists already processed.
     */
    function setNodesInTree(tree, treedata, replayCfgs, listCfg=null, lists=[]) {
        if (listCfg) {
            treedata = addListNode(tree, treedata, listCfg, lists);
        }
        for (let i=0; i<replayCfgs.length; i++) {
            cfg = replayCfgs[i];
            if (cfg.xpath.indexOf(']/') > -1) {
                setEmbeddedLists(tree, treedata, cfg, lists);
            }
            if (cfg.xpath.endsWith(']')) {
                return setNodesInTree(tree, treedata, replayCfgs.slice(i+1), cfg, lists);
            }
            treedata = addCfgNode(tree, treedata, cfg);
        }
    }

    /**
     * Helper function to populateReplay(), below - given a replay segment,
     * prepare to populate the JSTreeGrid with the contents of the replay.
     */
    function populateJSTreeReplay(segment,segmentTree=(yangtree.config.tree)) {
        if (!segment.yang.modules) {
            popDialog("Custom replay XML cannot be populated into the tree.");
            return;
        }
        let module = Object.keys(segment.yang.modules)[0];

        tree = $(segmentTree).jstree(true);
        if(tree == false)
          return false;

        rpc_ui.clearGrid();
        if (rpc_ui.config.addListNodesRpc.length > 0) {
            rpc_ui.removeAllTreeListEntry(tree, false);
            tree.redraw(true);
        }

        // Have to refresh the JSON because XPaths may change
        // as a result of previous value setting.
        let treedata = tree.get_json($(segmentTree),{flat: true, no_children: false});
        for (let i=0; i < treedata.length; i++) {
            if (treedata[i].text == module) {
                // This is the module branch we want to walk
                treedata = treedata.slice(i);
                break;
            }
        }

        let replayCfgs = segment.yang.modules[module].configs;

        setNodesInTree(tree, treedata, replayCfgs);

        tree.redraw(true);
        tree.deselect_all();
    }

    /**
     * Given structured replay data as returned by tasks.getTask(),
     * populate the UI accordingly, including reloading the jstree if needed,
     * then call rpcmanager.populateSavedRPCsFromReplay, populateJSTreeReplay().
     */
    function populateReplay(taskdata) {
        let progressBarDiv = startProgress($(config.progressBar), "", "",
                                           "Loading replay contents...");
        let modules = [];
        for (let segment of taskdata.task.segments) {
            /* Custom-RPC replays don't have listed modules */
            if (segment.yang.modules) {
                modules = modules.concat(Object.keys(segment.yang.modules));
            }
        }

        /* Sanity check - can we actually display the module(s) required? */
        for (let module of modules) {
            let opt = $(config.moduleSelect).find("option[value=" + module + "]");
            if (opt.length < 1) {
                popDialog('Module "' + module + '" not found in selected YANG set.' +
                          '\nPlease select a YANG set that includes this module.');
                stopProgress(progressBarDiv);
                return;
            }
        }

        rpcmanager.populateSavedRPCsFromReplay(taskdata.task.segments);

        /* Load the required modules, if not already loaded */
        let changedModules = false;
        let selection = $(config.moduleSelect).val() || [];
        for (let module of modules) {
            if (!selection.includes(module)) {
                changedModules = true;
            }
        }

        let lastSegment = taskdata.task.segments[taskdata.task.segments.length - 1];
        if (taskdata.task.segments.length > 1) {
            popDialog("Replay contains multiple segments (RPCs). " +
                      "The JSTree will be populated with the last one.");
            /* keep going, though */
        }
        /* Change the NETCONF operation if necessary */
        let protoOp = lastSegment.yang['proto-op'];
        $(config.protoOpSelect).val(protoOp);
        $(config.protoOpSelect).trigger("change");
        segmentTree = (yangtree.config.tree);

        if (changedModules) {
            $(config.moduleSelect).val(selection.concat(modules));
            $(config.moduleSelect).trigger("chosen:updated");

            /* TODO, the below is similar to code in netconf.html */
            $(".ys-module-required").removeClass("disabled");
            jsTree(['yang'], $(config.moduleSelect).val(),
                   $(config.yangsetSelect).val())
                .then(function() {
                    yangtree.pushExploreState($(config.yangsetSelect).val(),
                                              $(config.moduleSelect).val());
                });

            $(segmentTree).one('loaded_grid.jstree', function() {
                populateJSTreeReplay(lastSegment, segmentTree);
                stopProgress(progressBarDiv);
            });
        } else {
            populateJSTreeReplay(lastSegment, segmentTree);
            stopProgress(progressBarDiv);
        }
    };

    return {
        config: config,
        jsTree: jsTree,
        getProtocolOperation: getProtocolOperation,
        buildEditProtocolOperationMenu: buildEditProtocolOperationMenu,
        filterNodes: filterNodes,
        getDatastores: getDatastores,
        getAllDatastores: getAllDatastores,
        lockUnlockDatastore: lockUnlockDatastore,
        startEndSession: startEndSession,
        toggleSessionButton: toggleSessionButton,
        getCapabilities: getCapabilities,
        setLoggingLevel: setLoggingLevel,
        populateReplay: populateReplay,
    };
}();
