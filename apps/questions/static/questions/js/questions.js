var app = angular.module('questions', ['select-by-number', 'formgroup']);

// customizations for Django integration
app.config(['$httpProvider', '$interpolateProvider', function($httpProvider, $interpolateProvider) {
    // use {$ and $} as tags for angular
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');

    // set Django's CSRF Cookie and Header
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

app.factory('QuestionsService', ['$http', '$timeout', '$window', '$q', function($http, $timeout, $window, $q) {

    var service = {};

    /* private variables */

    var baseurl = angular.element('meta[name="baseurl"]').attr('content');

    var urls = {
        'catalogs': baseurl + 'api/questions/catalogs/',
        'sections': baseurl + 'api/questions/sections/',
        'subsections': baseurl + 'api/questions/subsections/',
        'question_entities': baseurl + 'api/questions/entities/',
        'questions': baseurl + 'api/questions/questions/',
        'questionsets': baseurl + 'api/questions/questionsets/',
        'widgettypes': baseurl + 'api/questions/widgettypes/',
        'attributes': baseurl + 'api/domain/attributes',
        'attribute_entities': baseurl + 'api/domain/entities',
        'options': baseurl + 'api/domain/options/',
        'ranges': baseurl + 'api/domain/ranges/',
        'conditions': baseurl + 'api/domain/conditions/',
        'valuestypes': baseurl + 'api/domain/valuestypes/',
        'relations': baseurl + 'api/domain/relations/',
    };

    /* private methods */

    function factory(ressource, parent) {
        if (ressource === 'catalogs') {
            return {
                'order': 0,
                'title_en': '',
                'title_de': ''
            };
        } else if (ressource === 'sections') {
            var section = {
                'order': 0,
                'title_en': '',
                'title_de': ''
            };

            if (angular.isDefined(parent) && parent) {
                section.catalog = parent.id;
            } else {
                section.catalog = null;
            }

            return section;
        } else if (ressource === 'subsections') {
            var subsection = {
                'order': 0,
                'title_en': '',
                'title_de': ''
            };

            if (angular.isDefined(parent) && parent) {
                subsection.section = parent.id;
            } else {
                subsection.section = null;
            }

            return subsection;
        } else if (ressource === 'questionsets') {
            var questionset = {
                'attribute_entity': null,
                'order': 0,
                'help_en': '',
                'help_de': ''
            };

            if (angular.isDefined(parent) && parent) {
                questionset.subsection = parent.id;
            } else {
                questionset.subsection = null;
            }

            return questionset;
        } else if (ressource === 'questions') {
            var question = {
                'attribute_entity': null,
                'order': 0,
                'text_en': '',
                'text_de': '',
                'help_en': '',
                'help_de': '',
                'widget_type': service.widgettypes[0].id
            };

            if (angular.isDefined(parent) && parent) {
                if (angular.isDefined(parent.is_set)) {
                    question.subsection = parent.subsection;
                    question.parent_entity = parent.id;
                } else {
                    question.subsection = parent.id;
                    question.parent_entity = null;
                }
            } else {
                question.subsection = null;
                question.parent_entity = null;
            }

            return question;
        }
    }

    function fetchCatalog() {
        return $http.get(urls.catalogs + service.current_catalog_id + '/', {
                params: {
                    nested: true
                }
            }).success(function(response) {
                service.catalog = response;
            });
    }

    function fetchItem(ressource, id) {
        return $http.get(urls[ressource] + id + '/').success(function(response) {
            service.values = response;
        });
    }

    function storeItem(ressource) {
        var promise;

        if (angular.isDefined(service.values.id)) {
            promise = $http.put(urls[ressource] + service.values.id + '/', service.values);
        } else {
            promise = $http.post(urls[ressource], service.values);
        }

        promise.error(function(response) {
            service.errors = response;
        });

        return promise;
    }

    function deleteItem(ressource) {
        return $http.delete(urls[ressource] + service.values.id + '/').error(function(response) {
            service.errors = response;
        });
    }

    function storeItems(ressource) {
        var promises = [];

        angular.forEach(service.values[ressource], function(item, index) {
            var promise = null;

            if (angular.isUndefined(item.attribute)) {
                item.attribute = service.values.id;
            }

            if (item.removed) {
                if (angular.isDefined(item.id)) {
                    promise = $http.delete(urls[ressource] + item.id + '/');
                }
            } else {
                if (angular.isDefined(item.id)) {
                    promise = $http.put(urls[ressource] + item.id + '/', item);
                } else {
                    promise = $http.post(urls[ressource], item);
                }
            }

            if (promise) {
                promise.error(function(response) {
                    service.errors[index] = response;
                });

                promises.push(promise);
            }
        });

        return $q.all(promises);
    }

    /* public methods */

    service.init = function() {
        var promises = [];

        promises.push($http.get(urls.widgettypes).success(function(response) {
            service.widgettypes = response;
        }));

        promises.push($http.get(urls.sections).success(function(response) {
            service.sections = response;
        }));

        promises.push($http.get(urls.subsections).success(function(response) {
            service.subsections = response;
        }));

        promises.push($http.get(urls.questionsets).success(function(response) {
            service.questionsets = response;
        }));

        promises.push($http.get(urls.attribute_entities).success(function(response) {
            service.attribute_entities = response;
        }));

        promises.push($http.get(urls.attributes).success(function(response) {
            service.attributes= response;
        }));

        promises.push($http.get(urls.catalogs).success(function(response) {
            service.catalogs = response;
            service.current_catalog_id = service.catalogs[0].id;

            fetchCatalog().success(function() {
                var current_scroll_pos = sessionStorage.getItem('current_scroll_pos');
                if (current_scroll_pos) {
                    $timeout(function() {
                        $window.scrollTo(0, current_scroll_pos);
                    });
                }
            });
        }));

        $window.addEventListener('beforeunload', function() {
            sessionStorage.setItem('current_scroll_pos', $window.scrollY);
        });

        return $q.all(promises);
    };

    service.changeCatalog = function() {
        fetchCatalog();
    };

    service.openFormModal = function(ressource, obj, create, copy) {

        service.errors = {};
        service.values = {};

        if (angular.isDefined(create) && create) {
            if (angular.isDefined(copy) && copy === true) {
                fetchItem(ressource, obj.id).then(function() {
                    delete service.values.id;
                });
            } else {
                service.values = factory(ressource, obj);
            }
        } else {
            fetchItem(ressource, obj.id);
        }

        $timeout(function() {
            $('#' + ressource + '-form-modal').modal('show');
        });
    };

    service.submitFormModal = function(ressource) {
        if (ressource === 'options' || ressource === 'conditions') {
            storeItems(ressource).then(function() {
                $('#' + ressource + '-form-modal').modal('hide');
                fetchEntities();
            });
        } else {
            storeItem(ressource).then(function(result) {

                if (ressource === 'catalogs') {
                    $http.get(urls.catalogs).success(function(response) {
                        service.catalogs = response;
                        service.current_catalog_id = result.data.id;
                        fetchCatalog();
                    });
                } else {
                    fetchCatalog();
                }

                $('#' + ressource + '-form-modal').modal('hide');
            });
        }
    };


                    //     angular.forEach(values.conditions, function(condition) {
                    //         if (condition.removed === true) {
                    //             deleteItem('conditions', condition);
                    //         } else {
                    //             condition.question_entity = response.id;
                    //             storeItem('conditions', condition);
                    //         }
                    //     });

                    //     angular.forEach(values.options, function(option) {
                    //         if (option.removed === true) {
                    //             deleteItem('options', option);
                    //         } else {
                    //             option.question = response.id;
                    //             if (angular.isUndefined(option.input_field)) {
                    //                 option.input_field = false;
                    //             }
                    //             storeItem('options', option);
                    //         }
                    //     });

                    //     angular.forEach(values.conditions, function(condition) {
                    //         if (condition.removed === true) {
                    //             deleteItem('conditions', condition);
                    //         } else {
                    //             condition.question_entity = response.id;
                    //             storeItem('conditions', condition);
                    //         }
                    //     });

    service.openDeleteModal = function(ressource, obj) {
        service.values = obj;
        $('#' + ressource + '-delete-modal').modal('show');
    };

    service.submitDeleteModal = function(ressource) {
        deleteItem(ressource).then(function(result) {
            if (ressource === 'catalogs') {
                $http.get(urls.catalogs).success(function(response) {
                    service.catalogs = response;
                    service.current_catalog_id = service.catalogs[0].id;
                    fetchCatalog();
                });
            } else {
                fetchCatalog();
            }
            $('#' + ressource + '-delete-modal').modal('hide');
        });
    };

    return service;

}]);

app.controller('QuestionsController', ['$scope', 'QuestionsService', function($scope, QuestionsService) {

    $scope.service = QuestionsService;
    $scope.service.init();

}]);
